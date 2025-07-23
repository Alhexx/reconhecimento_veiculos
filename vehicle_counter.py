import cv2
import time
import paho.mqtt.client as mqtt
import torch.serialization
import json
from ultralytics.nn.tasks import DetectionModel
from ultralytics import YOLO

MQTT_BROKER = "192.168.0.6"
MQTT_PORT = 1883
MQTT_TOPIC = "traffic/avenida1"
MQTT_USERNAME = "admin"
MQTT_PASSWORD = "admin"

LIMITE_VEICULOS = 10

INTERVALO_SEGUNDOS = 5
CLASSES_VEICULOS = [2, 3, 5, 7]  # carro, moto, onibus, caminhão

torch.serialization.add_safe_globals({'ultralytics.nn.tasks.DetectionModel': DetectionModel})

# MQTT opcional
# client = mqtt.Client()
# client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
# client.connect(MQTT_BROKER, MQTT_PORT, 60)
# client.loop_start()

model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture("Transito_pesado_2.mp4")

ultimo_processamento = 0
last_status = ""

while True:
    ret, frame = cap.read()

    # Se o vídeo acabar, reinicia
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    agora = time.time()
    if agora - ultimo_processamento >= INTERVALO_SEGUNDOS:
        ultimo_processamento = agora

        results = model(frame, stream=False, verbose=False)[0]

        veiculos = 0
        for cls in results.boxes.cls:
            if int(cls) in CLASSES_VEICULOS:
                veiculos += 1

        status = "intenso" if veiculos > LIMITE_VEICULOS else "livre"
        print(f"[DEBUG] Veículos: {veiculos} | Status: {status}")

        # Envia por MQTT somente se status mudar
        # if status != last_status:
        #     payload = json.dumps({
        #         "avenida": "Av. Exemplo",
        #         "status": status,
        #         "veiculos": veiculos
        #     })
        #     client.publish(MQTT_TOPIC, payload, qos=0)
        #     last_status = status

    frame_com_bboxes = results.plot()

    # Exibição
    cv2.putText(frame_com_bboxes, f"Veiculos: {veiculos}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
    cv2.imshow("Monitoramento", frame_com_bboxes)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
# client.loop_stop()
# client.disconnect()

