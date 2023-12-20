import whisper
import pydub
import pydub.effects
import shutil
import time


def float_to_s(f) -> str:    
        return str(round(f, 1)) + 's'


class VideoTranscribe:
    def __init__(self, videofile, out_tag) -> None:
        self.tag = out_tag
        self.modelpath = "../subtitles/models/local_whisper_model.pt"
        self.videofile = videofile
        self.localvideofile = f'{self.tag}.mp4'
        self.localaudiofile = f'{self.tag}.mp3'
        self.localrawtranscription = f'{self.tag}_r.txt'
        self.cudadevice = "cpu"


    
    def elapsed_time(self):    
        elapsed = time.time() - self.stime        
        return float_to_s(elapsed) 


    def run(self, progress):
        self.stime = time.time()

        progress(0.0, desc="Iniciando transcrição")
        shutil.copy(self.videofile, self.localvideofile)
        videosize = self.split_audio()
        progress(0.05, desc="Vídeo copiado e áudio separado. Carregando modelo PT-BR...")

        self.model = whisper.load_model(self.modelpath, device=self.cudadevice)
        progress(0.15, desc=f"Modelo carregado. Transcrição de vídeo de {videosize} de duração...")

        saida = self.model.transcribe(self.localaudiofile, language="pt", condition_on_previous_text=False, verbose=False)        
        progress(0.95, desc="Texto transcrito")

        texto = self.whisper_to_list(saida)
        texto_str = '\n'.join(texto)
        with open(self.localrawtranscription, 'w') as f:        
            f.write(texto_str)
        progress(1, desc="Texto salvo")

        fim = self.elapsed_time()
        return f"Pronto em {fim}. Texto disponível abaixo", texto_str
    

    def split_audio(self):        
        mp4_arq = pydub.AudioSegment.from_file(self.localvideofile, "mp4")
        mp4_gain = pydub.effects.normalize(mp4_arq)
        mp4_gain.export(self.localaudiofile, format="mp3")    
        video_size = len(mp4_gain)/1000
        return float_to_s(video_size)

           


    def whisper_to_list(self, saida):    
        infotexto = list()
        for segm in saida['segments']:
            i = segm['id']
            start = segm['start']
            end = segm['end']
            text = segm['text']
            elem = dict()
            elem['i'] = i
            elem['start'] = start
            elem['end'] = end    
            elem['text'] = text
            infotexto.append(elem)  
        texto = [x['text'] for x in infotexto]    
        self.infotexto = infotexto
        return texto
