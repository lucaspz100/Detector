import cv2
import numpy as np

# --- PASSO DE CONFIGURAÇÃO ---
# Ajuste os valores HSV para a cor da sua esfera.
# Exemplo para uma esfera VERMELHA. Vermelho é uma cor especial pois atravessa o 0 no círculo cromático HSV.
# Esta faixa funciona para a maioria dos vermelhos, mas pode precisar de ajuste.
limite_inferior_cor = np.array([80, 120, 70])
limite_superior_cor = np.array([150, 255, 255])
# Se não funcionar, tente a faixa alternativa para vermelhos mais escuros/vivos:
# limite_inferior_cor = np.array([170, 120, 70])
# limite_superior_cor = np.array([180, 255, 255])
# -----------------------------

# Inicia a captura de vídeo
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Erro: Não foi possível abrir a câmera.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Os primeiros passos são os mesmos
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mascara = cv2.inRange(hsv, limite_inferior_cor, limite_superior_cor)
    mascara = cv2.erode(mascara, None, iterations=2)
    mascara = cv2.dilate(mascara, None, iterations=2)
    contornos, _ = cv2.findContours(mascara.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Verifica se algum contorno foi encontrado
    if len(contornos) > 0:
        # Pega o maior contorno
        c = max(contornos, key=cv2.contourArea)
        
        # Filtra contornos pequenos para evitar ruído
        if cv2.contourArea(c) > 100: # Esferas podem parecer menores, ajuste se necessário
            # --- ANÁLISE PARA ESFERA ---
            # Encontra o círculo que envolve o contorno
            (x, y), raio = cv2.minEnclosingCircle(c)
            
            # Converte as coordenadas e o raio para inteiros para poder desenhar
            centro = (int(x), int(y))
            raio = int(raio)

            # Desenha o círculo e o centroide no frame original
            cv2.circle(frame, centro, raio, (0, 255, 0), 2) # Desenha o contorno do círculo
            cv2.circle(frame, centro, 5, (0, 0, 255), -1)   # Desenha o centro do círculo

            # Prepara e exibe o texto com as informações
            posicao_texto = f"Pos: ({centro[0]}, {centro[1]})"
            raio_texto = f"Raio: {raio} pixels"
            
            cv2.putText(frame, posicao_texto, (centro[0] - 80, centro[1] - raio - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, raio_texto, (centro[0] - 80, centro[1] - raio - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)


    # Mostra os frames
    cv2.imshow('Frame Original com Esfera', frame)
    cv2.imshow('Mascara de Cor', mascara)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()