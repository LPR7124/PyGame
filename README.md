# AutoFox: Autorama Arcade 2 Jogadores
PyGame 2026.1
Usamos o código base disponivel em:
https://github.com/techwithtim/Pygame-Car-Racer.git

## Membros da Equipe - Turma A
* Ana Luiza Marsilio Alves
* Lívia Pinheiro Rodrigues
* Maria Vitória Gomes Rametta

## Tecnologias e Créditos de Co-Criação (IA)
Este projeto foi desenvolvido com o suporte de ferramentas de Inteligência Artificial para otimização de código e geração de assets, divididos da seguinte forma:
* **Física e Lógica do Mapeador (`mapeador.py`):** Desenvolvido em co-criação com o **Google Gemini**, que auxiliou na estruturação dos algoritmos matemáticos de interpolação de curvas e cálculo vetorial de faixas paralelas (`offset_closed_polyline`).
* **Design Visual e Iteração de Código:** Suporte técnico do **Google Gemini** na refatoração, modularização de arquivos e implementação de feedbacks dinâmicos de áudio.
* **Assets de Imagem (Arte e Interface):** As telas de menu retrô (Capa, Escolha de Carros, Telas de Instrução) e os elementos visuais do jogo foram gerados e refinados utilizando o **ChatGPT (OpenAI / DALL-E)**.

## Trilhas Sonoras e Efeitos Sonoros (SFX)
Para construir a atmosfera de corrida arcade inspirada na cultura automotiva, este projeto acadêmico utiliza músicas comerciais sob a doutrina de **Uso Educacional / Fair Use** (sem fins lucrativos). Todos os direitos pertencem aos seus respectivos autores e gravadoras:
* **Música Tema da Corrida (`principal_sixdays.mp3`):** *Six Days* (DJ Shadow / Mos Def).
* **Música Ambiente dos Menus (`principal.mp3`):** *Tokyo Drift* (Teriyaki Boyz).
* **Efeitos Sonoros (`escolher_carro.mp3` e `carro_morrendo.mp3`):** SFXs de interface e motor obtidos em bancos de áudio gratuitos.
*Nota: Este projeto tem caráter estritamente acadêmico para a disciplina de Design de Software. Os áudios não serão comercializados e estão integrados nativamente através do módulo `pygame.mixer`.*

## Sobre o Projeto
O AutoFox é um simulador de autorama estilo arcade para dois jogadores desenvolvido inteiramente em Python. O jogo desafia os jogadores a controlarem a velocidade de seus veículos em pistas sinuosas. Acelerar demais nas curvas fará o carro descarrilar, aplicando uma punição de tempo! O projeto conta com:
* Interface retrô pixel art e trilha sonora dinâmica.
* Seleção de veículos com atributos únicos.
* Sistema de física para cálculo de velocidade, descarrilamento e curvas.
* Múltiplas fases com níveis de dificuldade crescentes.

## Apresentação em Vídeo
[Clique aqui para assistir ao vídeo de demonstração do jogo no YouTube](https://youtu.be/u6QqQqq8Eww)

## Pré-requisitos e Instalação
Antes de rodar o jogo, certifique-se de ter o [Python](https://www.python.org/) e a biblioteca PyGame (pip install pygame) instalados em sua máquina.
* Após clonagem do repositório, o jogo deve ser executado a partir do arquivo principal geral/main.py

## Controles
* Player 1 (Azul): Setas (<- / ->) para navegar no menu. Segure SETA PARA CIMA ou ESPAÇO para acelerar na pista.
* Player 2 (Vermelho): A e D para navegar no menu. Segure W para acelerar na pista.
