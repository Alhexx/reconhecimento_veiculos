import cv2
import time
import paho.mqtt.client as mqtt
import torch.serialization
import json
from ultralytics.nn.tasks import DetectionModel
from ultralytics import YOLO
import datetime

MQTT_BROKER = "107.172.94.10"
MQTT_PORT = 1883
MQTT_TOPIC = "traffic/raw/prudente_de_moraes"
# MQTT_USERNAME = "admin"
# MQTT_PASSWORD = "admin"

LIMITE_VEICULOS_LEVE = 15
LIMITE_VEICULOS_MODERADO = 25
LIMITE_VEICULOS_PESADO = 45

INTERVALO_SEGUNDOS = 5
CLASSES_VEICULOS = [2, 3, 5, 7]  # carro, moto, onibus, caminhão

torch.serialization.add_safe_globals({'ultralytics.nn.tasks.DetectionModel': DetectionModel})

# MQTT opcional
client = mqtt.Client()
# client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.connect(MQTT_BROKER)
client.loop_start()

model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture("Transito_leve.mp4")

ultimo_processamento = 0
last_status = ""

while True:
	ret, frame = cap.read()

	# Se o vídeo acabar, reinicia
	if not ret:
		cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
		continue

	# agora = time.time()
	# if agora - ultimo_processamento >= INTERVALO_SEGUNDOS:
	# 	ultimo_processamento = agora

	results = model(frame, stream=False, verbose=False)[0]

	veiculos = 0
	for cls in results.boxes.cls:
			if int(cls) in CLASSES_VEICULOS:
					veiculos += 1
	
	if veiculos <= LIMITE_VEICULOS_LEVE:
			status = "low"
	elif LIMITE_VEICULOS_LEVE < veiculos <= LIMITE_VEICULOS_MODERADO:
			status = "medium"
	elif LIMITE_VEICULOS_MODERADO < veiculos <= LIMITE_VEICULOS_PESADO:
			status = "high"
	# print(f"[DEBUG] Veículos: {veiculos} | Status: {status}")

	# Envia por MQTT somente se status mudar
	if status != last_status:
		payload = {
				"device_id": "rasp_prudente_de_moraes",
				"timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat() + "Z",
				"street_id": "prudente_de_moraes",
				"vehicle_count": veiculos,
				"congestion_level": status
		}
		print(payload)

		mensagem = json.dumps(payload)
		client.publish(MQTT_TOPIC, mensagem, qos=0, retain=True)
		last_status = status

	frame_com_bboxes = results.plot()

	# Exibição
	cv2.putText(frame_com_bboxes, f"Veiculos: {veiculos}", (10, 30),
							cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
	
	cv2.putText(frame_com_bboxes,f"Transito: {status}", (10, 60),
							cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
	
	cv2.imshow("Monitoramento", frame_com_bboxes)

	if cv2.waitKey(1) & 0xFF == ord('q'):
			break

cap.release()
cv2.destroyAllWindows()
client.loop_stop()
client.disconnect()

