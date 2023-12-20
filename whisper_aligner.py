import stable_whisper
import time
import json


def float_to_s(f) -> str:    
        return str(round(f, 1)) + 's'


class SubtitileAligner:
    def __init__(self, texto_ajustado, out_tag) -> None:
        self.modelpath = "../subtitles/models/local_whisper_model.pt"
        self.cudadevice = "cpu"
        self.tag = out_tag        
        self.aligned_text = texto_ajustado
        self.localvideofile = f'{self.tag}.mp4'
        self.localaudiofile = f'{self.tag}.mp3'
        self.localrawtranscription = f'{self.tag}_r.txt'
        self.outputvideofile = f'{self.tag}_o.mp4'
        self.wordingdict = f'{out_tag}_w.json'


    def define_altura(self, altura):
        self.altura_legenda = altura
        
         
    def align(self, model):
        saida = model.align(self.localaudiofile, self.aligned_text, language="pt", original_split=True, regroup=False)
        whisper_result = saida.to_dict()
        whisper_wrs = whisper_result['segments']
        wrs_count_segments = len(whisper_wrs)
        return whisper_wrs, wrs_count_segments
        
    
    def elapsed_time(self):    
        elapsed = time.time() - self.stime        
        return float_to_s(elapsed) 


    def run(self, progress):
        self.stime = time.time()

        progress(0.0, desc="Sincronização de legenda. Carregando modelo PT-BR...")
        model = stable_whisper.load_model(self.modelpath, device=self.cudadevice)   
        
        progress(0.15, desc=f"Modelo carregado. Sincronia de legenda...")
        wrsegm, count = self.align(model)
        self.define_wording(count, wrsegm)
                
        progress(0.30, desc="Timestamps por palavras gerado. Iniciando renderização...")
        subs = fancy_subtitles(altura=self.altura_legenda)
        subs.load_main(self.localvideofile)
        for i in range(count):
            txtdict, textline = self.processa_segmento_whisper(wrsegm, i)
            subs.subtitle_line(txtdict, textline)

        subs.render(self.outputvideofile, self.localaudiofile)

        fim = self.elapsed_time()
        print(f"Pronto em {fim}. Vídeo disponível para download")
        return self.outputvideofile


    def define_wording(self, wrs_count_segments, whisper_wrs):
        wording = dict()
        for i in range(wrs_count_segments):
            txtdict, textline = self.processa_segmento_whisper(whisper_wrs, i)
            wording[i] = {'n': textline, 'dict': txtdict}
        with open(self.wordingdict, 'w') as f:
            json.dump(wording, f)



    def processa_segmento_whisper(self, whisper_wrs, index):    
        wrs = whisper_wrs[index]    
        text_end = wrs['end']
        if index % 2 == 0:
            showline = 1
            if index+1 < len(whisper_wrs):
                text_end = whisper_wrs[index+1]['end']
        else:
            showline = 2        
        txtline = dict()
        txtline['line'] = wrs['text'].strip()
        txtline['start']  = wrs['start']
        txtline['duration'] = text_end - wrs['start']
        count_words = len(wrs['words'])
        txtline['count'] = count_words
        for i in range(count_words):
            txtline[i] = dict()
            txtline[i]['word'] = wrs['words'][i]['word'].strip()
            txtline[i]['start'] = wrs['words'][i]['start']
            txtline[i]['duration'] = wrs['words'][i]['end'] - wrs['words'][i]['start']
        return txtline, showline





from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip

class fancy_subtitles:
    def __init__(self, altura=770, fonte=60) -> None:        
        self.clip_list = list()
        
        # parametrizados 
        self.F_SIZE = fonte
        self.F_COR = 'white'
        self.BG_COR = [0, 0, 0]   
        self.toptext = altura

        # calculados
        self.MARGIN_X = int(self.F_SIZE/10)
        self.MARGIN_Y = int(self.F_SIZE/20)
        self.bg_height = int(self.F_SIZE*1.4)

        # tamanho do espaço. Pode ser calculado
        self.BLANK_X = 14

        # do sistema
        self.threads = 6


    def top_text(self, textline):
        return int(self.toptext + self.F_SIZE*1.5*textline)


    def load_main(self, arq_video):
        main_video = VideoFileClip(arq_video, target_resolution=(1280, 720))
        self.clip_list.append(main_video)
        self.VIDEO_X = main_video.size[0]
        self.duration = main_video.duration     
        self.fps = main_video.fps


    def subtitle_line(self, txtdict, textline=1):
        txt = txtdict['line']
        txt_start = txtdict['start']
        txt_duration = txtdict['duration']
        text_y_pos = self.top_text(textline)

        txt_clip = (TextClip(txt, fontsize=self.F_SIZE, font="Roboto", color=self.F_COR, stroke_width=.5, stroke_color=self.F_COR)
                        .set_position(('center', text_y_pos))
                        .set_start(txt_start)
                        .set_duration(txt_duration))
        txt_x = txt_clip.size[0]
        # redefine variaveis da legenda de acordo com esta linha
        bg_pos_x = (self.VIDEO_X - txt_x) // 2 - self.MARGIN_X
        bg_pos_y = text_y_pos - self.MARGIN_Y        
        for i in range(txtdict['count']):            
            bg_pos_x = self.subtitle_word(txtdict[i], bg_pos_x, bg_pos_y)
        self.clip_list.append(txt_clip)



    def subtitle_word(self, txtitem, bg_pos_x, bg_pos_y):
        w = txtitem['word']
        temp_clip = TextClip(w, fontsize=60, font="Roboto", color='white')
        temp_x = temp_clip.size[0]

        sta = txtitem['start']
        dur = txtitem['duration']
        bg_width = temp_x + 2*self.MARGIN_X

        bg_clip = (ColorClip(size =(bg_width, self.bg_height), color=self.BG_COR)
                        .set_position((bg_pos_x, bg_pos_y))
                        .set_start(sta)
                        .set_duration(dur)                        
                  )
        self.clip_list.append(bg_clip)
        return bg_pos_x + temp_x + self.BLANK_X        
    

    def render(self, arq_saida, arq_audio):
        result = CompositeVideoClip(self.clip_list, size=(720, 1280))
        result.duration = self.duration
        result.write_videofile(arq_saida, fps=self.fps, audio=arq_audio, codec="libx264", audio_codec="libmp3lame", threads=self.threads)
    
        
