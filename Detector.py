import cv2
import numpy as np
import time
import math

# ... (Configuração de cor e câmera como antes) ...
limite_inferior_cor = np.array([0, 190, 96])
limite_superior_cor = np.array([15, 255, 255])
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("Erro: Não foi possível abrir a câmera.")
    exit()

# Variáveis de estado
posicao_anterior = None
tempo_anterior = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # ... (Processamento de imagem e detecção de contornos como antes) ...
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mascara = cv2.inRange(hsv, limite_inferior_cor, limite_superior_cor)
    mascara = cv2.erode(mascara, None, iterations=2)
    mascara = cv2.dilate(mascara, None, iterations=2)
    contornos, _ = cv2.findContours(mascara.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contornos) > 0:
        c = max(contornos, key=cv2.contourArea)
        if cv2.contourArea(c) > 100:
            (x, y), raio = cv2.minEnclosingCircle(c)
            centro_atual = (int(x), int(y))
            
            # Só fazemos cálculos se tivermos uma posição anterior
            if posicao_anterior is not None:
                tempo_atual = time.time()
                delta_tempo = tempo_atual - tempo_anterior
                
                # Vetor velocidade em pixels por frame
                dx = centro_atual[0] - posicao_anterior[0]
                dy = centro_atual[1] - posicao_anterior[1]

                # Evita cálculos se a esfera estiver parada
                if dx != 0 or dy != 0 and delta_tempo > 0:
                    
                    # --- 1. CÁLCULO DO MÓDULO ---
                    distancia_pixels = math.sqrt(dx**2 + dy**2)
                    modulo_pps = distancia_pixels / delta_tempo
                    texto_modulo = f"Modulo: {int(modulo_pps)} pps"
                    cv2.putText(frame, texto_modulo, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                    
                    # --- 2. CÁLCULO DA DIREÇÃO (ÂNGULO) ---
                    # Usamos atan2(-dy, dx) para um ângulo cartesiano padrão
                    angulo_rad = math.atan2(-dy, dx)
                    direcao_graus = math.degrees(angulo_rad)
                    texto_direcao = f"Direcao: {direcao_graus:.1f} graus"
                    cv2.putText(frame, texto_direcao, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                    
                    # --- 3. DESENHO DO SENTIDO (SETA) ---
                    # Normaliza o vetor para ter comprimento 1
                    vetor_unitario_dx = dx / distancia_pixels
                    vetor_unitario_dy = dy / distancia_pixels
                    
                    # Define um comprimento fixo para a seta ser visível
                    comprimento_seta = 75
                    ponto_final_x = centro_atual[0] + int(vetor_unitario_dx * comprimento_seta)
                    ponto_final_y = centro_atual[1] + int(vetor_unitario_dy * comprimento_seta)
                    
                    # Desenha a seta vermelha representando o vetor velocidade
                    cv2.arrowedLine(frame, centro_atual, (ponto_final_x, ponto_final_y), (0, 0, 255), 3)

            # Atualiza o estado para o próximo frame
            posicao_anterior = centro_atual
            tempo_anterior = time.time()

            # Desenha o contorno da esfera
            cv2.circle(frame, centro_atual, int(raio), (0, 255, 0), 2)
    else:
        # Se não detectar a esfera, reseta o estado
        posicao_anterior = None
        
    cv2.imshow('Vetor Velocidade', frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()