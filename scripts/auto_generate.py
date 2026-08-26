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

    def __init__(self, script_file, output_dir="output"):
        self.script_file = Path(script_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # 子目录
        self.audio_dir = self.output_dir / "audio"
        self.video_dir = self.output_dir / "video"
        self.final_dir = self.output_dir / "final"

        for d in [self.audio_dir, self.video_dir, self.final_dir]:
            d.mkdir(exist_ok=True)

        # 加载脚本
        with open(self.script_file, 'r', encoding='utf-8') as f:
            self.script = json.load(f)

        self.scenes = self.script['scenes']
        self.voice = self.script.get('voice', 'zh-CN-XiaoxiaoNeural')

        # ComfyUI API
        self.comfyui_url = "http://127.0.0.1:8188"

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
            frames_needed = round(duration_seconds * 24)
            length = max(5, frames_needed) + (5 - (max(5, frames_needed) % 17)) % 17

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
                "inputs": {"samples": ["140", 0], "vae": ["122", 0]}
            },
            "124": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["139", 0], "vae": ["121", 0]}
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
            "139": {
                "class_type": "easy cleanGpuUsed",
                "inputs": {"anything": ["127", 0]}
            },
            "140": {
                "class_type": "easy cleanGpuUsed",
                "inputs": {"anything": ["127", 0]}
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

            response = requests.post(
                f"{self.comfyui_url}/prompt",
                json=payload
            )

            if response.status_code == 200:
                prompt_id = response.json()['prompt_id']
                prompt_ids.append({
                    "scene_id": scene['id'],
                    "prompt_id": prompt_id
                })
                print(f"   ✅ 已提交: {prompt_id}")
            else:
                print(f"   ❌ 提交失败")

        print()
        print(f"✨ 已提交 {len(prompt_ids)} 个任务")

        # 保存提交记录
        submission_file = self.output_dir / "submissions.json"
        with open(submission_file, 'w') as f:
            json.dump(prompt_ids, f, indent=2)

        return prompt_ids

    def wait_for_completion(self, prompt_ids, check_interval=300):
        """等待所有视频生成完成"""
        print()
        print("=" * 80)
        print("⏳ 等待视频生成完成...")
        print("=" * 80)
        print()

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

                except Exception:
                    pass

            if len(completed) < len(prompt_ids):
                time.sleep(check_interval)

        elapsed = time.time() - start_time
        print()
        print(f"✨ 所有视频生成完成！耗时: {elapsed/60:.1f} 分钟")

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
                "[0:a]volume=0.5[env];[1:a]volume=1.2[narr];[env][narr]amix=inputs=2:duration=first[aout]",
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

    args = parser.parse_args()

    generator = VideoStoryGenerator(args.script, args.output)
    asyncio.run(generator.run_full_pipeline())


if __name__ == "__main__":
    main()