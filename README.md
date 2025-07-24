# Arquitetura e Tópicos MQTT

## Componentes

1. Edge (Raspberry Pi + câmera)  
   - Captura frame
   - Calcula status do congestionamento via reconhecimento de imagens
   - Publica um JSON em MQTT com parametros de consgestionamento 

2. Broker MQTT  
   - Recebe e roteia topicos de mensagem

3. Backend  
   - Inscreve‑se nos tópicos  
   - Valida o payload  
   - Persiste no banco  
   - Disponibiliza dados via REST/GraphQL visando dashboards 

4. Display (ESP32)  
   - Inscrito no tópico  
   - Recebe as mensagens em tempo real  
   - Atualiza o painel de trânsito  


## Tópicos MQTT

- traffic/raw/{street_id} 
  Publica os dados brutos de contagem (vehicle_count) do sensor.

- traffic/all/health  
  Keep‑alive / heartbeat periódico de todos os dispositivos.

- traffic/status/{street_id}  
  Publica o status de congestionamento (“baixa”/“média”/“alta”) após classificação pelo backend.

## Payloads

### 1. traffic/raw/{street_id}

```json
{
  "device_id":     "esp32-01",
  "timestamp":     "2025-07-23T22:15:00Z",
  "street_id":     "prudente_de_moraes",
  "vehicle_count": 12,
  "congestion_level": "high" (high or medium or low)
}
```

---

### 2. traffic/all/health

```json
{
  "device_id": "esp32-01",
  "timestamp": "2025-07-23T22:15:10Z",
  "status":    "online",
  "uptime_s":  3600
}
```

---

### 3. traffic/status/{street_id}

```json
{
  "device_id":        "esp32-01",
  "timestamp":        "2025-07-23T22:15:05Z",
  "street_id":        "prudente_de_moraes",
  "congestion_level": "média"
}
```