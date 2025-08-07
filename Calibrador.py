import cv2
import numpy as np

def nada(x):
    # Função vazia necessária para a criação da trackbar
    pass

# Inicia a captura de vídeo
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("Erro: Não foi possível abrir a câmera.")
    exit()

# Cria uma janela para as trackbars
cv2.namedWindow("Trackbars")

# Cria as trackbars para os limites de cor HSV
# O valor máximo para H (Hue) no OpenCV é 179
cv2.createTrackbar("H Min", "Trackbars", 0, 179, nada)
cv2.createTrackbar("H Max", "Trackbars", 179, 179, nada)
cv2.createTrackbar("S Min", "Trackbars", 0, 255, nada)
cv2.createTrackbar("S Max", "Trackbars", 255, 255, nada)
cv2.createTrackbar("V Min", "Trackbars", 0, 255, nada)
cv2.createTrackbar("V Max", "Trackbars", 255, 255, nada)

while True:
    # Captura o frame da câmera
    ret, frame = cap.read()
    if not ret:
        break

    # Converte o frame para o espaço de cores HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Pega os valores atuais das trackbars
    h_min = cv2.getTrackbarPos("H Min", "Trackbars")
    h_max = cv2.getTrackbarPos("H Max", "Trackbars")
    s_min = cv2.getTrackbarPos("S Min", "Trackbars")
    s_max = cv2.getTrackbarPos("S Max", "Trackbars")
    v_min = cv2.getTrackbarPos("V Min", "Trackbars")
    v_max = cv2.getTrackbarPos("V Max", "Trackbars")

    # Monta os arrays de limite inferior e superior
    limite_inferior = np.array([h_min, s_min, v_min])
    limite_superior = np.array([h_max, s_max, v_max])

    # Cria a máscara com base nos limites
    mascara = cv2.inRange(hsv, limite_inferior, limite_superior)
    
    # Mostra o frame original e a máscara resultante
    cv2.imshow("Frame Original", frame)
    cv2.imshow("Mascara", mascara)

    # Condição de saída (tecla ESC)
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Imprime os valores finais para você copiar
print(f"limite_inferior_cor = np.array([{h_min}, {s_min}, {v_min}])")
print(f"limite_superior_cor = np.array([{h_max}, {s_max}, {v_max}])")

cap.release()
cv2.destroyAllWindows()