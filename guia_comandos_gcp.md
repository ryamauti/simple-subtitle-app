Estou testando em uma máquina EC2 de 16 GB RAM e 4 vcpus. 
Acho que precisaria ter mais vcpus para ter melhor performance.
Recomendo armazenar o modelo em um bucket storage na mesma cloud.

### Processo de inicialização
Uma vez só:
```
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3-venv ffmpeg imagemagick git
git clone https://github.com/ryamauti/simple-subtitle-app.git
mkdir pyenv
python3 -m venv pyenv/
gcloud storage cp gs://modelos-videos/local_whisper_model.pt ./simple-subtitle-app/models
```

Uma vez só, também é preciso alterar uma configuração do ImageMagick:
  Abrir o `/etc/ImageMagick-6/policy.xml`
  e comentar com `<!-- -->` esta linha: 
  `<policy domain="path" rights="read | write" pattern="@*"/>`


### Ativação da VENV
Toda vez será necessário ativar o ambiente
```
source pyenv/bin/activate
cd simple-subtitle-app

python app.py
```

No entanto, os requirements já devem estar instalados
```
pip install -r requirements.txt

```




