"""Video Generator — Create short-form videos with text, visuals, and voiceover.

Generates platform-ready videos:
- Text overlay on dynamic backgrounds
- AI voiceover (edge-tts, free)
- Trending-style visuals
- Platform-specific aspect ratios and timing
"""

import json
import logging
import os
import random
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Platform video specs
PLATFORM_SPECS = {
    "tiktok": {
        "width": 1080,
        "height": 1920,
        "fps": 30,
        "aspect": "9:16",
        "max_duration": 180,
        "font_size": 64,
        "font_color": "white",
        "outline_color": "black",
        "outline_width": 3,
    },
    "youtube_shorts": {
        "width": 1080,
        "height": 1920,
        "fps": 30,
        "aspect": "9:16",
        "max_duration": 60,
        "font_size": 60,
        "font_color": "white",
        "outline_color": "black",
        "outline_width": 2,
    },
    "instagram_reels": {
        "width": 1080,
        "height": 1920,
        "fps": 30,
        "aspect": "9:16",
        "max_duration": 90,
        "font_size": 56,
        "font_color": "white",
        "outline_color": "black",
        "outline_width": 2,
    },
}


@dataclass
class VideoConfig:
    """Configuration for video generation."""
    platform: str = "tiktok"
    width: int = 1080
    height: int = 1920
    fps: int = 30
    font_size: int = 64
    font_color: str = "white"
    background_style: str = "gradient"  # gradient, solid, particles, zoom
    voiceover: bool = True
    voice: str = "en-US-AriaNeural"  # Edge TTS voice
    music_volume: float = 0.15
    text_animation: str = "fade"  # fade, slide, pop, typewriter
    caption_style: str = "centered"  # centered, bottom, karaoke

    @classmethod
    def for_platform(cls, platform: str) -> "VideoConfig":
        specs = PLATFORM_SPECS.get(platform, PLATFORM_SPECS["tiktok"])
        return cls(
            platform=platform,
            width=specs["width"],
            height=specs["height"],
            fps=specs["fps"],
            font_size=specs["font_size"],
        )


class BackgroundGenerator:
    """Generate dynamic video backgrounds."""
    
    STYLES = ["gradient", "solid", "particles", "zoom", "pulse"]
    
    @staticmethod
    def generate_gradient(width: int, height: int, duration: float, 
                          fps: int, colors: list[tuple] = None) -> str:
        """Generate an animated gradient background."""
        output_path = tempfile.mktemp(suffix=".mp4")
        
        # TikTok-style dark gradient combos (top color → bottom color)
        palettes = [
            ("#1a1a2e", "#16213e"),  # Deep blue
            ("#0f0f23", "#1a1a3e"),  # Dark purple
            ("#0a1628", "#162040"),  # Midnight
            ("#1a0a2e", "#2d1b4e"),  # Purple haze
            ("#0d1117", "#1a2332"),  # GitHub dark
        ]
        top, bottom = random.choice(palettes)
        
        # Use gradient filter (much simpler and reliable)
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"gradients=s={width}x{height}:d={duration}:speed=0.5:"
                   f"c0={top}:c1={bottom}:x0=0:y0=0:x1=0:y1={height}:nb_colors=2",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
            "-pix_fmt", "yuv420p",
            "-t", str(duration),
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                return output_path
            else:
                # Fallback to solid
                logger.debug(f"Gradient failed, trying solid. stderr: {result.stderr.decode()[:200]}")
                return BackgroundGenerator.generate_solid(width, height, duration, fps)
        except Exception as e:
            logger.debug(f"Gradient generation failed: {e}")
            return BackgroundGenerator.generate_solid(width, height, duration, fps)

    @staticmethod
    def generate_solid(width: int, height: int, duration: float,
                       fps: int, color: tuple = None) -> str:
        """Generate a solid color background."""
        if color is None:
            colors = ["rgb(20,20,40)", "rgb(10,10,30)", "rgb(0,20,50)", "rgb(30,10,40)", "rgb(15,15,35)"]
            color = random.choice(colors)
        else:
            r, g, b = color
            color = f"rgb({r},{g},{b})"
        
        output_path = tempfile.mktemp(suffix=".mp4")
        
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c={color}:s={width}x{height}:d={duration}:r={fps}",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
            "-pix_fmt", "yuv420p",
            "-t", str(duration),
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=20)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                return output_path
            else:
                logger.debug(f"Solid bg: file not created or empty. stderr: {result.stderr.decode()[:200]}")
        except Exception as e:
            logger.debug(f"Solid background failed: {e}")
        
        return ""
    
    @staticmethod
    def generate_particles(width: int, height: int, duration: float,
                           fps: int) -> str:
        """Generate a particle/starfield effect background."""
        output_path = tempfile.mktemp(suffix=".mp4")
        
        # Dark background with floating particles (noise-based)
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c=black:s={width}x{height}:d={duration}:r={fps}",
            "-f", "lavfi",
            "-i", f"noise=alls=20:allf=t+u:s={width}x{height}:d={duration}:r={fps}",
            "-filter_complex",
            "[0][1]blend=all_mode=screen:all_opacity=0.3,"
            f"geq=r='if(lt(random(1)*100,2),255,r(X,Y)*0.98)':"
            f"g='if(lt(random(1)*100,2),255,g(X,Y)*0.98)':"
            f"b='if(lt(random(1)*100,2),200,b(X,Y)*0.95)'",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
            "-t", str(duration),
            output_path
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, timeout=30)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                return output_path
        except Exception as e:
            logger.debug(f"Particles background failed: {e}")
        
        return ""


class TextOverlayRenderer:
    """Render animated text overlays on video."""
    
    @staticmethod
    def render_hook_text(hook: str, width: int, height: int, duration: float,
                         font_size: int = 64, style: str = "fade") -> str:
        """Render the hook text as a transparent video layer."""
        output_path = tempfile.mktemp(suffix=".mp4")
        
        # Escape special characters for ffmpeg drawtext
        safe_text = hook.replace("'", "\u2019").replace(":", " -").replace('"', "'")
        # Limit text length
        if len(safe_text) > 60:
            safe_text = safe_text[:57] + "..."
        
        filter_str = (
            f"drawtext=text='{safe_text}':fontsize={font_size}:fontcolor=white:"
            f"borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2"
        )
        
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c=black@0:s={width}x{height}:d={duration}:r=30",
            "-vf", filter_str + ",format=yuva420p",
            "-c:v", "libx264", "-preset", "ultrafast",
            "-pix_fmt", "yuva420p",
            "-t", str(duration),
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=15)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 500:
                return output_path
            else:
                logger.debug(f"Hook text stderr: {result.stderr.decode()[:300]}")
        except Exception as e:
            logger.debug(f"Hook text render failed: {e}")
        
        return ""
    
    @staticmethod
    def render_script_text(script_lines: list[str], width: int, height: int,
                           total_duration: float, font_size: int = 48) -> str:
        """Render script text with timed subtitles."""
        output_path = tempfile.mktemp(suffix=".mp4")
        
        lines_per_segment = max(1, len(script_lines))
        segment_duration = total_duration / lines_per_segment
        
        filters = []
        for i, line in enumerate(script_lines[:6]):  # Max 6 lines
            start_time = round(i * segment_duration, 2)
            end_time = round((i + 1) * segment_duration, 2)
            safe_line = line.replace("'", "\u2019").replace(":", " -").replace('"', "'")[:50]
            
            y_offset = -40 + (i % 3) * 40
            y_expr = f"(h-text_h)/2+{y_offset}" if y_offset != 0 else "(h-text_h)/2"
            
            filters.append(
                f"drawtext=text='{safe_line}':fontsize={font_size}:fontcolor=white:"
                f"borderw=2:bordercolor=black:x=(w-text_w)/2:y={y_expr}:"
                f"enable='between(t,{start_time},{end_time})'"
            )
        
        if not filters:
            return ""
        
        filter_str = ",".join(filters)
        
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c=black@0:s={width}x{height}:d={total_duration}:r=30",
            "-vf", filter_str + ",format=yuva420p",
            "-c:v", "libx264", "-preset", "ultrafast",
            "-pix_fmt", "yuva420p",
            "-t", str(total_duration),
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=20)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 500:
                return output_path
            else:
                logger.debug(f"Script text stderr: {result.stderr.decode()[:300]}")
        except Exception as e:
            logger.debug(f"Script text render failed: {e}")
        
        return ""


class VoiceoverGenerator:
    """Generate AI voiceover using edge-tts (free, no API key)."""
    
    VOICES = {
        "narrator_female": "en-US-AriaNeural",
        "narrator_male": "en-US-GuyNeural",
        "energetic_female": "en-US-JennyNeural",
        "energetic_male": "en-US-ChristopherNeural",
        "calm_female": "en-US-MonicaNeural",
        "calm_male": "en-US-BrandonNeural",
    }
    
    @classmethod
    async def generate(cls, text: str, voice: str = "narrator_female",
                       speed: float = 1.1) -> str:
        """Generate voiceover audio file."""
        output_path = tempfile.mktemp(suffix=".mp3")
        
        voice_id = cls.VOICES.get(voice, cls.VOICES["narrator_female"])
        
        try:
            import edge_tts
            communicate = edge_tts.Communicate(text, voice_id, rate=f"+{int((speed-1)*100)}%")
            await communicate.save(output_path)
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 500:
                logger.info(f"Voiceover generated: {len(text)} chars")
                return output_path
        except ImportError:
            logger.debug("edge-tts not installed, skipping voiceover")
        except Exception as e:
            logger.debug(f"Voiceover generation failed: {e}")
        
        return ""
    
    @classmethod
    def generate_sync(cls, text: str, voice: str = "narrator_female",
                      speed: float = 1.1) -> str:
        """Synchronous wrapper for voiceover generation."""
        import asyncio
        return asyncio.run(cls.generate(text, voice, speed))


class VideoComposer:
    """Compose final video from components."""
    
    def __init__(self, config: VideoConfig = None):
        self.config = config or VideoConfig()
        self.bg_gen = BackgroundGenerator()
        self.text_renderer = TextOverlayRenderer()
    
    def compose(self, hook: str, script: str, caption: str,
                duration_seconds: int, output_path: str = None) -> str:
        """Compose a complete video from content."""
        from moviepy import VideoFileClip, CompositeVideoClip, AudioFileClip
        import numpy as np
        
        if output_path is None:
            output_path = f"output/video_{random.randint(1000,9999)}.mp4"
        
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        duration = min(duration_seconds, 60)  # Cap at 60s for shorts
        w, h = self.config.width, self.config.height
        
        logger.info(f"Composing {duration}s video ({w}x{h}) for {self.config.platform}")
        
        temp_files = []
        
        try:
            # 1. Generate background
            bg_style = self.config.background_style
            if bg_style == "gradient":
                bg_path = self.bg_gen.generate_gradient(w, h, duration, self.config.fps)
            elif bg_style == "particles":
                bg_path = self.bg_gen.generate_particles(w, h, duration, self.config.fps)
            else:
                bg_path = self.bg_gen.generate_solid(w, h, duration, self.config.fps)
            
            if not bg_path:
                # Fallback: solid dark background
                bg_path = self.bg_gen.generate_solid(w, h, duration, self.config.fps)
            
            if bg_path:
                temp_files.append(bg_path)
                bg_clip = VideoFileClip(bg_path)
            else:
                # Ultimate fallback: numpy array
                bg_clip = VideoFileClip(
                    self._make_solid_clip(w, h, duration, self.config.fps)
                )
            
            # 2. Add hook text (first 3 seconds prominently)
            hook_duration = min(3.0, duration * 0.3)
            hook_text = self.text_renderer.render_hook_text(
                hook, w, h, hook_duration,
                self.config.font_size, self.config.text_animation
            )
            
            clips = [bg_clip]
            
            if hook_text:
                temp_files.append(hook_text)
                hook_clip = VideoFileClip(hook_text).with_start(0).with_duration(hook_duration)
                clips.append(hook_clip)
            
            # 3. Add script text (after hook)
            if duration > 4:
                script_lines = [l.strip() for l in script.split("\n") if l.strip() and not l.startswith(("HOOK:", "CTA:"))]
                if script_lines:
                    script_duration = duration - hook_duration - 1
                    script_text = self.text_renderer.render_script_text(
                        script_lines[:6], w, h, script_duration,
                        self.config.font_size - 12
                    )
                    if script_text:
                        temp_files.append(script_text)
                        script_clip = VideoFileClip(script_text).with_start(hook_duration)
                        clips.append(script_clip)
            
            # 4. Compose
            final = CompositeVideoClip(clips, size=(w, h))
            final = final.with_duration(duration)
            
            # 5. Add voiceover if available
            voiceover_path = None
            try:
                voiceover_path = VoiceoverGenerator.generate_sync(
                    f"{hook}. {' '.join(script.split(chr(10))[:4])}",
                    speed=1.15
                )
                if voiceover_path and os.path.exists(voiceover_path):
                    temp_files.append(voiceover_path)
                    audio = AudioFileClip(voiceover_path)
                    if audio.duration > duration:
                        audio = audio.subclipped(0, duration)
                    final = final.with_audio(audio)
                    logger.info("Voiceover added to video")
            except Exception as e:
                logger.debug(f"Voiceover skipped: {e}")
            
            # 6. Write output
            final.write_videofile(
                output_path,
                fps=self.config.fps,
                codec="libx264",
                audio_codec="aac",
                preset="ultrafast",
                threads=2,
                logger=None,
            )
            
            final.close()
            bg_clip.close()
            
            file_size = os.path.getsize(output_path)
            logger.info(f"Video saved: {output_path} ({file_size / 1024:.0f} KB)")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Video composition failed: {e}")
            import traceback
            traceback.print_exc()
            return ""
        
        finally:
            # Cleanup temp files
            for f in temp_files:
                try:
                    if os.path.exists(f):
                        os.remove(f)
                except:
                    pass
    
    def _make_solid_clip(self, w: int, h: int, duration: float, fps: int) -> str:
        """Create a solid color video as ultimate fallback."""
        output_path = tempfile.mktemp(suffix=".mp4")
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c=rgb(20,20,40):s={w}x{h}:d={duration}:r={fps}",
            "-c:v", "libx264", "-preset", "ultrafast",
            output_path
        ]
        subprocess.run(cmd, capture_output=True, timeout=15)
        return output_path


class VideoGenerator:
    """Main video generation interface."""
    
    def __init__(self, platform: str = "tiktok"):
        self.config = VideoConfig.for_platform(platform)
        self.composer = VideoComposer(self.config)
    
    def generate(self, content: dict, output_path: str = None) -> str:
        """
        Generate a video from a content piece.
        
        Args:
            content: Dict with hook, script, caption, duration_seconds
            output_path: Where to save the video
        
        Returns:
            Path to generated video
        """
        hook = content.get("hook", "")
        script = content.get("script", "")
        caption = content.get("caption", "")
        duration = content.get("duration_seconds", 30)
        
        if output_path is None:
            output_path = f"output/{self.config.platform}_{random.randint(1000,9999)}.mp4"
        
        return self.composer.compose(hook, script, caption, duration, output_path)
    
    def generate_batch(self, content_list: list[dict], output_dir: str = "output") -> list[str]:
        """Generate multiple videos."""
        os.makedirs(output_dir, exist_ok=True)
        
        paths = []
        for i, content in enumerate(content_list):
            path = os.path.join(output_dir, f"video_{i+1:03d}.mp4")
            result = self.generate(content, path)
            if result:
                paths.append(result)
        
        logger.info(f"Generated {len(paths)}/{len(content_list)} videos")
        return paths
