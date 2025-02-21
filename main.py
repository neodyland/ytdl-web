from yt_dlp import YoutubeDL
from pathlib import Path
from typing import List, Tuple

tmp = Path("./tmp")


def download(url: str, audio_only: bool, state: List[str]) -> Tuple[str, List[str]]:
    if url == "":
        return
    if not tmp.exists():
        tmp.mkdir(exist_ok=True, parents=True)
    opt = {
        "format": "bestaudio*" if audio_only else "bestvideo*+bestaudio/best",
        "noplaylist": True,
        "outtmpl": str(tmp / "%(id)s.%(ext)s"),
        "prefer_ffmpeg": True,
    }
    if audio_only:
        opt["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
            }
        ]
    with YoutubeDL(opt) as dl:
        info = dl.extract_info(url, download=True)
        fp = dl.prepare_filename(info)
    state.append(fp)
    return fp, state


def delete(state: List[str]):
    for v in state:
        Path(v).unlink(missing_ok=True)


import gradio as gr


with gr.Blocks(title="Simple Youtube Downloader GUI") as demo:
    gr.Markdown("# Simple Youtube Downloader GUI")
    state = gr.State(value=[], delete_callback=lambda v: delete(v))
    path = gr.State(value="")
    with gr.Row():
        with gr.Column():
            with gr.Row():
                url = gr.Textbox(label="Youtube URL")
                audio = gr.Checkbox(label="Audio only")
            with gr.Row():
                dl = gr.Button(value="Download", variant="primary")
        with gr.Column():

            @gr.render(inputs=(audio, path))
            def f(audio, path):
                if not path or path == "":
                    return gr.Text("Nothing to show for now...")
                if audio:
                    return gr.Audio(value=path)
                else:
                    return gr.Video(value=path)

    dl.click(download, [url, audio, state], [path, state], concurrency_limit=5)
    audio.change(lambda: "", [], [path])
    url.change(lambda: "", [], [path])

demo.launch(server_name="0.0.0.0", server_port=7860, show_api=False)
