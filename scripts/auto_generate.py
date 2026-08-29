#!/usr/bin/env python3
"""
AI短视频自动化制作 - 完整流程脚本
从脚本到成片的全自动化生成
"""

import argparse
import json
import asyncio
import edge_tts
import requests
import time
import subprocess
from pathlib import Path
from datetime import datetime
import shutil

class VideoStoryGenerator:
    """AI短视频生成器"""

    def __init__(self, script_file, output_dir="output", comfyui_url=None, comfyui_output_dir=None, voice=None,
                 width=1344, height=768, steps=20, narration_volume=1.2, ambient_volume=0.5):
        self.script_file = Path(script_file) if script_file else None
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # 子目录
        self.audio_dir = self.output_dir / "audio"
        self.video_dir = self.output_dir / "video"
        self.final_dir = self.output_dir / "final"

        for d in [self.audio_dir, self.video_dir, self.final_dir]:
            d.mkdir(exist_ok=True)

        # 加载脚本（如果提供了文件）
        if self.script_file and self.script_file.exists():
            with open(self.script_file, 'r', encoding='utf-8') as f:
                self.script = json.load(f)
        else:
            self.script = None

        # 参数设置
        self.scenes = self.script['scenes'] if self.script else []
        self.voice = voice or (self.script.get('voice', 'zh-CN-XiaoxiaoNeural') if self.script else 'zh-CN-XiaoxiaoNeural')

        # 视频参数
        self.width = width
        self.height = height
        self.steps = steps

        # 音频参数
        self.narration_volume = narration_volume
        self.ambient_volume = ambient_volume

        # ComfyUI API - 支持外部链接
        self.comfyui_url = comfyui_url or "http://127.0.0.1:8188"
        print(f"🔌 ComfyUI地址: {self.comfyui_url}")

        # 验证 ComfyUI 连接
        try:
            response = requests.get(f"{self.comfyui_url}/system_stats", timeout=5)
            if response.status_code == 200:
                print(f"✅ ComfyUI 连接成功")
            else:
                print(f"⚠️  ComfyUI 响应异常: HTTP {response.status_code}")
        except Exception as e:
            print(f"⚠️  无法连接 ComfyUI: {e}")
            print(f"   请确保 ComfyUI 已启动并运行在 {self.comfyui_url}")

        # ComfyUI 输出目录 - 优先使用参数，否则尝试自动检测
        self.comfyui_output_dir = comfyui_output_dir
        if not self.comfyui_output_dir:
            # 如果没有指定，检查是否可以访问默认路径
            default_path = "/workspace/output"
            if Path(default_path).exists():
                self.comfyui_output_dir = default_path
                print(f"📁 ComfyUI输出目录: {self.comfyui_output_dir} (自动检测)")
            else:
                self.comfyui_output_dir = None
                print(f"📁 ComfyUI输出目录: 未指定（将通过 API 下载视频）")
                print(f"   💡 这通常发生在 ComfyUI 部署在远程服务器时")
        else:
            print(f"📁 ComfyUI输出目录: {self.comfyui_output_dir} (自定义)")

    async def generate_narration_audio(self):
        """阶段1: 生成解说词音频"""
        print("=" * 80)
        print("🎙️ 阶段1: 生成解说词音频")
        print("=" * 80)
        print()

        audio_files = []

        for scene in self.scenes:
            text = scene['narration']
            output_file = self.audio_dir / f"narration_{scene['id']:02d}.mp3"

            print(f"正在生成场景 {scene['id']}: {text[:40]}...")

            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(str(output_file))

            print(f"✅ 已保存: {output_file}")
            audio_files.append({
                "scene_id": scene['id'],
                "audio_file": str(output_file)
            })

        print()
        print(f"✨ 音频生成完成: {len(audio_files)} 个文件")
        return audio_files

    def get_audio_durations(self):
        """获取所有音频时长"""
        from mutagen.mp3 import MP3

        print()
        print("=" * 80)
        print("📊 计算音频时长")
        print("=" * 80)
        print()

        total_duration = 0
        scene_timing = []

        for scene in self.scenes:
            audio_file = self.audio_dir / f"narration_{scene['id']:02d}.mp3"
            audio = MP3(str(audio_file))
            duration_seconds = audio.info.length
            total_duration += duration_seconds

            # 计算MiniMax H3要求的帧数
            # MiniMax H3 要求 length ≡ 1 (mod 17)，即 1, 18, 35, 52, ...
            frames_needed = round(duration_seconds * 24)
            # 向上对齐到最近的 17n+1，最小值为 18 (17*1+1)
            length = max(18, ((frames_needed - 1 + 16) // 17) * 17 + 1)

            scene_timing.append({
                "scene_id": scene['id'],
                "duration_seconds": round(duration_seconds, 2),
                "length": length,
                "audio_file": str(audio_file)
            })

            print(f"场景 {scene['id']:02d}: {duration_seconds:5.2f}秒 ({length:3d}帧)")

        print()
        print(f"总时长: {total_duration:.2f}秒 ({total_duration/60:.2f}分钟)")

        # 保存时长信息
        timing_file = self.audio_dir / "scene_timing.json"
        with open(timing_file, 'w', encoding='utf-8') as f:
            json.dump({
                "total_duration_seconds": round(total_duration, 2),
                "total_duration_minutes": round(total_duration / 60, 2),
                "scenes": scene_timing
            }, f, indent=2)

        return scene_timing

    def create_workflow(self, scene, timing):
        """创建单个场景的ComfyUI工作流"""
        return {
            "121": {
                "class_type": "VAELoader",
                "inputs": {"vae_name": "minimax_h3_video_vae_fp16.safetensors"}
            },
            "122": {
                "class_type": "VAELoader",
                "inputs": {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}
            },
            "123": {
                "class_type": "VAEDecodeAudio",
                "inputs": {"samples": ["127", 0], "vae": ["122", 0]}
            },
            "124": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["127", 0], "vae": ["121", 0]}
            },
            "125": {
                "class_type": "KSamplerSelect",
                "inputs": {"sampler_name": "res_multistep"}
            },
            "126": {
                "class_type": "BasicScheduler",
                "inputs": {
                    "denoise": 1,
                    "model": ["129", 0],
                    "scheduler": "simple",
                    "steps": 20
                }
            },
            "127": {
                "class_type": "SamplerCustomAdvanced",
                "inputs": {
                    "noise": ["131", 0],
                    "guider": ["128", 0],
                    "sampler": ["125", 0],
                    "sigmas": ["126", 0],
                    "latent_image": ["133", 1]
                }
            },
            "128": {
                "class_type": "BasicGuider",
                "inputs": {
                    "model": ["129", 0],
                    "conditioning": ["133", 0]
                }
            },
            "129": {
                "class_type": "UNETLoader",
                "inputs": {
                    "unet_name": "minimax_h3_fl2va_int8_convrot.safetensors",
                    "weight_dtype": "default"
                }
            },
            "130": {
                "class_type": "CLIPLoader",
                "inputs": {
                    "clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
                    "type": "minimax",
                    "device": "default"
                }
            },
            "131": {
                "class_type": "RandomNoise",
                "inputs": {"noise_seed": scene['id'] * 1000000 + 123456789}
            },
            "132": {
                "class_type": "CreateVideo",
                "inputs": {
                    "images": ["124", 0],
                    "audio": ["123", 0],
                    "fps": 24,
                    "bit_depth": 8
                }
            },
            "133": {
                "class_type": "MiniMaxH3ImageToVideo",
                "inputs": {
                    "clip": ["130", 0],
                    "vae": ["121", 0],
                    "width": 1344,
                    "height": 768,
                    "length": timing['length'],
                    "prompt": f"{scene['visual_prompt']}, {scene['audio']}"
                }
            },
            "92": {
                "class_type": "SaveVideo",
                "inputs": {
                    "video": ["132", 0],
                    "filename_prefix": f"video/scene_{scene['id']:02d}",
                    "format": "auto",
                    "format.codec": "auto"
                }
            }
        }

    def check_minimax_models(self):
        """检查 MiniMax H3 模型是否存在"""
        print()
        print("=" * 80)
        print("🔍 检查 MiniMax H3 模型")
        print("=" * 80)
        print()

        try:
            response = requests.get(f"{self.comfyui_url}/object_info", timeout=10)
            if response.status_code == 200:
                object_info = response.json()

                # 检查必需的模型
                required_models = {
                    "UNETLoader": ["minimax_h3_fl2va_int8_convrot.safetensors"],
                    "CLIPLoader": ["qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"],
                    "VAELoader": [
                        "minimax_h3_video_vae_fp16.safetensors",
                        "minimax_h3_audio_vae_fp32.safetensors"
                    ]
                }

                all_ok = True
                for node_type, model_names in required_models.items():
                    if node_type in object_info:
                        available_models = object_info[node_type].get('input', {}).get('required', {}).get('unet_name' if node_type == 'UNETLoader' else 'clip_name' if node_type == 'CLIPLoader' else 'vae_name', [[]])[0]

                        for model_name in model_names:
                            if model_name in available_models:
                                print(f"✅ {model_name}")
                            else:
                                print(f"❌ {model_name} - 未找到")
                                all_ok = False
                    else:
                        print(f"❌ {node_type} - 节点类型未找到")
                        all_ok = False

                if not all_ok:
                    print()
                    print("⚠️  缺少必需的模型，请先下载 MiniMax H3 模型")
                    return False

                print()
                print("✨ 所有模型检查通过")
                return True
            else:
                print(f"❌ 无法获取模型信息: HTTP {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ 检查模型失败: {e}")
            return False

    def submit_all_videos(self, scene_timing):
        """阶段2: 提交所有视频生成任务"""
        print()
        print("=" * 80)
        print("🎬 阶段2: 提交视频生成任务")
        print("=" * 80)
        print()

        prompt_ids = []

        for scene, timing in zip(self.scenes, scene_timing):
            print(f"提交场景 {scene['id']:02d}...")

            workflow = self.create_workflow(scene, timing)
            payload = {"prompt": workflow}

            print(f"   提交工作流到: {self.comfyui_url}/prompt")

            try:
                response = requests.post(
                    f"{self.comfyui_url}/prompt",
                    json=payload,
                    timeout=30
                )

                if response.status_code == 200:
                    prompt_id = response.json()['prompt_id']
                    prompt_ids.append({
                        "scene_id": scene['id'],
                        "prompt_id": prompt_id
                    })
                    print(f"   ✅ 已提交: {prompt_id}")
                else:
                    print(f"   ❌ 提交失败: HTTP {response.status_code}")
                    print(f"   响应内容: {response.text[:200]}")
            except Exception as e:
                print(f"   ❌ 提交异常: {e}")
                print(f"   请检查 ComfyUI 是否正在运行")

        print()
        print(f"✨ 已提交 {len(prompt_ids)} 个任务")

        # 保存提交记录
        submission_file = self.output_dir / "submissions.json"
        with open(submission_file, 'w') as f:
            json.dump(prompt_ids, f, indent=2)

        return prompt_ids

    def wait_for_completion(self, prompt_ids, check_interval=60):
        """等待所有视频生成完成"""
        print()
        print("=" * 80)
        print("⏳ 等待视频生成完成...")
        print("=" * 80)
        print()

        print(f"💡 检查间隔: {check_interval}秒")

        start_time = time.time()
        completed = set()

        while len(completed) < len(prompt_ids):
            for item in prompt_ids:
                if item['prompt_id'] in completed:
                    continue

                try:
                        response = requests.get(
                            f"{self.comfyui_url}/history/{item['prompt_id']}"
                        )

                        if response.status_code == 200:
                            history = response.json()

                            if item['prompt_id'] in history:
                                status = history[item['prompt_id']].get('status', {})
                                if status.get('completed', False):
                                    completed.add(item['prompt_id'])
                                    print(f"✅ 场景 {item['scene_id']:02d} 完成")

                except Exception as e:
                    print(f"⚠️  检查任务状态失败: {e}")

            if len(completed) < len(prompt_ids):
                time.sleep(check_interval)

        elapsed = time.time() - start_time
        print()
        print(f"✨ 所有视频生成完成！耗时: {elapsed/60:.1f} 分钟")
        print()

        # 获取视频文件到项目输出目录
        print("📋 获取视频文件到项目目录...")
        self.retrieve_videos_from_comfyui(prompt_ids)

    def retrieve_videos_from_comfyui(self, prompt_ids):
        """从 ComfyUI 获取视频文件（支持文件系统复制和 API 下载）"""
        comfyui_output = Path(self.comfyui_output_dir)

        print(f"   ComfyUI 输出目录: {comfyui_output}")
        print(f"   目录存在: {comfyui_output.exists()}")

        # 方式 1: 尝试文件系统复制
        if comfyui_output.exists():
            print(f"   ✅ 使用文件系统复制方式")
            self._copy_videos_from_filesystem(prompt_ids, comfyui_output)
        else:
            # 方式 2: 通过 API 下载
            print(f"   ⚠️  ComfyUI 输出目录不可访问，尝试通过 API 下载")
            print(f"   💡 这通常发生在 ComfyUI 部署在远程服务器时")
            self._download_videos_via_api(prompt_ids)

    def _copy_videos_from_filesystem(self, prompt_ids, comfyui_output):
        """通过文件系统复制视频"""
        # 列出 ComfyUI 输出目录中的所有视频
        all_videos = list(comfyui_output.rglob("*.mp4"))
        print(f"   找到 {len(all_videos)} 个视频文件")

        for item in prompt_ids:
            scene_id = item['scene_id']

            # 在 ComfyUI 输出目录查找视频
            video_pattern = f"scene_{scene_id:02d}_*.mp4"
            print(f"   搜索模式: {video_pattern}")

            videos = list(comfyui_output.rglob(video_pattern))
            print(f"   找到 {len(videos)} 个匹配文件")

            if videos:
                # 找到最新的视频
                latest_video = max(videos, key=lambda x: x.stat().st_mtime)

                # 复制到项目目录
                dest_file = self.video_dir / latest_video.name
                try:
                    shutil.copy(str(latest_video), str(dest_file))
                    print(f"   ✅ 场景 {scene_id:02d}: {latest_video.name}")
                    print(f"      从: {latest_video}")
                    print(f"      到: {dest_file}")
                except Exception as e:
                    print(f"   ❌ 复制失败: {e}")
            else:
                print(f"   ⚠️  场景 {scene_id:02d}: 未找到视频文件")
                # 尝试其他搜索方式
                all_scene_videos = [v for v in all_videos if f"scene_{scene_id:02d}" in str(v) or f"_{scene_id:02d}_" in str(v)]
                if all_scene_videos:
                    print(f"   💡 可能的视频文件:")
                    for v in all_scene_videos[:3]:
                        print(f"      - {v.name}")

        print()

    def _download_videos_via_api(self, prompt_ids):
        """通过 ComfyUI API 下载视频"""
        print(f"   正在从 {self.comfyui_url} 下载视频...")

        for item in prompt_ids:
            scene_id = item['scene_id']
            prompt_id = item['prompt_id']

            print(f"   处理场景 {scene_id:02d} (任务ID: {prompt_id})...")

            try:
                # 获取任务历史记录
                response = requests.get(f"{self.comfyui_url}/history/{prompt_id}", timeout=10)
                if response.status_code != 200:
                    print(f"      ❌ 无法获取任务历史: HTTP {response.status_code}")
                    continue

                history = response.json()
                if prompt_id not in history:
                    print(f"      ❌ 任务历史中未找到此任务")
                    continue

                # 从历史记录中获取输出文件
                outputs = history[prompt_id].get('outputs', {})

                for node_id, output in outputs.items():
                    videos = output.get('videos', [])
                    for video_info in videos:
                        filename = video_info.get('filename')
                        subfolder = video_info.get('subfolder', '')
                        video_type = video_info.get('type', 'output')

                        if filename and filename.endswith('.mp4'):
                            # 构建下载 URL
                            params = {
                                'filename': filename,
                                'type': video_type,
                                'subfolder': subfolder
                            }

                            # 下载视频
                            try:
                                download_response = requests.get(
                                    f"{self.comfyui_url}/view",
                                    params=params,
                                    timeout=60,
                                    stream=True
                                )

                                if download_response.status_code == 200:
                                    # 保存视频
                                    dest_file = self.video_dir / filename
                                    with open(dest_file, 'wb') as f:
                                        for chunk in download_response.iter_content(chunk_size=8192):
                                            f.write(chunk)

                                    print(f"      ✅ 已下载: {filename} ({dest_file.stat().st_size / 1024 / 1024:.2f} MB)")
                                else:
                                    print(f"      ❌ 下载失败: HTTP {download_response.status_code}")
                            except Exception as e:
                                print(f"      ❌ 下载失败: {e}")

            except Exception as e:
                print(f"      ❌ 处理失败: {e}")

        print()

    def mix_audio(self):
        """阶段3: 混合音频"""
        print()
        print("=" * 80)
        print("🔊 阶段3: 混合音频")
        print("=" * 80)
        print()

        timing_file = self.audio_dir / "scene_timing.json"
        with open(timing_file, 'r') as f:
            timing = json.load(f)

        for scene_info in timing['scenes']:
            scene_id = scene_info['scene_id']

            # 找到生成的视频文件
            video_files = list(self.video_dir.glob(f"scene_{scene_id:02d}_*.mp4"))
            if not video_files:
                print(f"⚠️ 场景 {scene_id:02d} 的视频文件未找到")
                continue

            video_file = video_files[0]
            audio_file = self.audio_dir / f"narration_{scene_id:02d}.mp3"
            output_file = self.final_dir / f"scene_{scene_id:02d}_mixed.mp4"

            print(f"混合场景 {scene_id:02d}...")

            # ffmpeg混合命令
            cmd = [
                "ffmpeg", "-y",
                "-i", str(video_file),
                "-i", str(audio_file),
                "-filter_complex",
                f"[0:a]volume={self.ambient_volume}[env];[1:a]volume={self.narration_volume}[narr];[env][narr]amix=inputs=2:duration=first[aout]",
                "-map", "0:v", "-map", "[aout]",
                "-c:v", "copy", "-c:a", "aac",
                str(output_file)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"   ✅ 完成: {output_file.name}")
            else:
                print(f"   ❌ 失败: {result.stderr[:100]}")

        print()
        print("✨ 音频混合完成！")

    def compose_final_video(self):
        """阶段4: 合成最终视频"""
        print()
        print("=" * 80)
        print("🎬 阶段4: 合成最终视频")
        print("=" * 80)
        print()

        # 创建场景列表文件
        scenes_file = self.final_dir / "scenes_list.txt"

        with open(scenes_file, 'w') as f:
            for scene in self.scenes:
                scene_file = self.final_dir / f"scene_{scene['id']:02d}_mixed.mp4"
                if scene_file.exists():
                    f.write(f"file '{scene_file}'\n")

        # 最终视频文件名
        title = self.script['title']
        final_video = self.final_dir / f"{title}_final.mp4"

        print(f"合成最终视频: {final_video.name}...")

        # ffmpeg合成命令
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(scenes_file),
            "-c", "copy",
            str(final_video)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print()
            print("=" * 80)
            print("🎉 全流程完成！")
            print("=" * 80)
            print()
            print(f"📹 最终视频: {final_video}")
            print(f"📊 标题: {title}")
            print(f"📊 场景数: {len(self.scenes)}")

            timing_file = self.audio_dir / "scene_timing.json"
            with open(timing_file, 'r') as f:
                timing = json.load(f)

            print(f"📊 时长: {timing['total_duration_minutes']:.2f} 分钟")
            print()
            print("✨ 享受您的AI生成短片！")
            print("=" * 80)

            return final_video
        else:
            print(f"❌ 合成失败: {result.stderr[:200]}")
            return None

    async def run_full_pipeline(self):
        """运行完整流程"""
        print("=" * 80)
        print(f"🎬 AI短视频生成器 - {self.script['title']}")
        print("=" * 80)
        print()
        print(f"📝 场景数: {len(self.scenes)}")
        print(f"🎤 TTS语音: {self.voice}")
        print(f"📁 输出目录: {self.output_dir}")
        print()

        # 阶段1: 生成音频
        await self.generate_narration_audio()

        # 检查模型（警告但不中断流程）
        print()
        print("⚠️  即将检查 MiniMax H3 模型...")
        models_ok = self.check_minimax_models()
        if not models_ok:
            print()
            print("⚠️  警告: 部分模型未找到，但将继续尝试生成")
            print("   如果生成失败，请检查模型是否正确安装")
        else:
            print()
            print("✅ 所有模型检查通过")

        # 获取音频时长
        scene_timing = self.get_audio_durations()

        # 阶段2: 生成视频
        prompt_ids = self.submit_all_videos(scene_timing)

        # 等待完成
        self.wait_for_completion(prompt_ids)

        # 阶段3: 混合音频
        self.mix_audio()

        # 阶段4: 合成最终视频
        final_video = self.compose_final_video()

        return final_video


def main():
    parser = argparse.ArgumentParser(description="AI短视频自动化制作")
    parser.add_argument("script", help="脚本JSON文件路径")
    parser.add_argument("--output", "-o", default="output", help="输出目录")

    # ComfyUI设置
    parser.add_argument("--comfyui-url", default=None,
                        help="ComfyUI服务器地址（默认: http://127.0.0.1:8188）")
    parser.add_argument("--comfyui-output-dir", default=None,
                        help="ComfyUI输出目录（默认: /workspace/output）")

    # 视频参数
    parser.add_argument("--width", type=int, default=1344, help="视频宽度")
    parser.add_argument("--height", type=int, default=768, help="视频高度")
    parser.add_argument("--steps", type=int, default=20, help="采样步数")

    # 音频参数
    parser.add_argument("--voice", default="zh-CN-XiaoxiaoNeural",
                        help="TTS语音 (zh-CN-XiaoxiaoNeural/zh-CN-YunxiNeural/zh-CN-YunjianNeural)")
    parser.add_argument("--narration-volume", type=float, default=1.2,
                        help="解说词音量倍数 (默认: 1.2)")
    parser.add_argument("--ambient-volume", type=float, default=0.5,
                        help="环境音音量倍数 (默认: 0.5)")

    args = parser.parse_args()

    generator = VideoStoryGenerator(
        script_file=args.script,
        output_dir=args.output,
        comfyui_url=args.comfyui_url,
        comfyui_output_dir=args.comfyui_output_dir,
        voice=args.voice,
        width=args.width,
        height=args.height,
        steps=args.steps,
        narration_volume=args.narration_volume,
        ambient_volume=args.ambient_volume
    )
    asyncio.run(generator.run_full_pipeline())


if __name__ == "__main__":
    main()