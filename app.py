import gradio as gr
from whisper_transcriber import VideoTranscribe as Vtran
from text_splitter import text_splitter
from whisper_aligner import SubtitileAligner as SAlign

# Functions
def squaredraw(nivel, altura_legenda_var, video_pos_top):    
    tmp = video_pos_top.zfill(16)
    vid_right = int(tmp[:4])    
    vid_left = int(tmp[4:7])
    vid_top = int(tmp[7:10])
    flag_left = int(tmp[10:13])
    flag_top = int(tmp[13:])

    distancia_flag_vid = vid_top - flag_top
    tam_video_y = int(1080/4)
    tam_video_x = int(720//4)
    degraus_nivel = 10
    delta_x = 16

    n_transform = distancia_flag_vid + nivel * tam_video_y / degraus_nivel    
    n = int(n_transform)    

    x = 0
    # se eles não estão alinhados:
    if flag_left - vid_left > 100:
        x = int(-tam_video_x / 2) - delta_x
    else:
        largura = vid_right - vid_left
        x = int(largura/2 - tam_video_x / 2 - delta_x / 2)

    # print(vid_left, vid_top, flag_left, flag_top, n)
    altura_legenda_var = nivel * 90
    style = f"'position: absolute; top: {n}px; left: {x}px;'"
    return gr.HTML(f"<div class='square' style={style}></div>", visible=True, elem_id='flag'), altura_legenda_var   


def load_audio():
    return gr.Audio('temp.mp3')                   ## TEMP !!!


def reloadtext():    
    with open('temp_r.txt', 'r') as f:            ## TEMP !!!        
        texto = f.read()
    return texto


def gera_legenda(texto_revisado):
    resultado = text_splitter(texto_revisado)    
    return '\n'.join(resultado)


# custom javascript
jsvR = 'document.getElementById("vid").getBoundingClientRect().right'
jsvL = 'document.getElementById("vid").getBoundingClientRect().left'
jsvT = 'document.getElementById("vid").getBoundingClientRect().top'
jsfL = 'document.getElementById("flag").getBoundingClientRect().left'
jsfT = 'document.getElementById("flag").getBoundingClientRect().top'


js_obj = '() => {' + f'return String(parseInt({jsvR})*1000000000000 + parseInt({jsvL})*1000000000 + parseInt({jsvT})*1000000 + parseInt({jsfL})*1000 + parseInt({jsfT})*1);' + '}'
    
customcss = """
.gradio-container video {
  position:relative;
  width: 180px; 
  height: 320px;
  margin: auto;
}
.square {
  width: 180px;
  height: 50px;
  background-color: yellow; 
  opacity: 0.2;
}
"""


# ------------------------
# --- GRADIO Interface ---

demo = gr.Blocks(css=customcss)    
with demo:
    altura_legenda_var = gr.State(730)    
    
    # Accordion's
    parte1 = gr.Accordion("1. Vídeo inicial e altura da legenda", open=True)
    parte2 = gr.Accordion("2. Ajustes no texto da transcrição", open=False)
    parte3 = gr.Accordion("3. Ajustes no vídeo final e download", open=False)

    with parte1:
        def video_progress(video, progress=gr.Progress()):                
            vt = Vtran(video, 'temp')                      ## TEMP !!!
            log, texto = vt.run(progress=progress)
            return log, texto     
                
        video_pos_elem = gr.Textbox(value=0, visible=False)
        vid = gr.Video(elem_id='vid')            
        btnvideo = gr.Button("Transcrever", variant='primary')    
        
        info_slider = "Escolha a posição da legenda, definindo a altura através da barra abaixo"
        slider = gr.Slider(0, 10, value=8, label="Posicionar legenda", info=info_slider)        
        x = gr.Interface(squaredraw, inputs=[slider, altura_legenda_var, video_pos_elem], outputs=["html", altura_legenda_var], live=True, allow_flagging=None)
        slider.change(None, outputs=video_pos_elem, js=js_obj)
        progresstranscribe = gr.Textbox(show_label=False)

    with parte2:        
        audio = gr.Audio()    
        text = gr.Textbox(label="Transcrição. Alterar aqui de acordo com o que se queira", interactive=True, autoscroll=False, lines=10)
        with gr.Row():
            btnaud = gr.Button("Carregar audio").click(fn=load_audio, inputs=None, outputs=audio)
            btntxt = gr.Button("Reverter texto", variant='stop').click(fn=reloadtext, inputs=None, outputs=text)
            btngen = gr.Button("Confirmar e gerar", variant='primary')

    btnvideo.click(fn=video_progress, inputs=vid, outputs=[progresstranscribe, text])

    with parte3:    
        def render_progress(texto_ajustado, altura_leg, progress=gr.Progress()):                
            sa = SAlign(texto_ajustado, 'temp')                      ## TEMP !!!            
            sa.define_altura(altura_leg)
            video = sa.run(progress=progress)
            return video     

        textsplit = gr.Textbox(label="Transcrição dividida linha por linha da exibição.", interactive=True, autoscroll=False, lines=20)        
        with gr.Row():
            btnvalidate = gr.Button("Validar alterações")
            btnrender = gr.Button("Renderizar", variant='primary')        
        videosaida = gr.Video(show_share_button=True)        

    btngen.click(fn=gera_legenda, inputs=text, outputs=textsplit)
    btnrender.click(fn=render_progress, inputs=[textsplit, altura_legenda_var], outputs=videosaida)

    
if __name__ == "__main__":    
    demo.launch(show_error=True, share=False, server_name="0.0.0.0", server_port=7860)






