# 🏥 Mapa 3D - Visualització Interactiva del Sistema Sanitari de Girona

Visualització interactiva 3D del sistema sanitari de la Regió Sanitària de Girona utilitzant CesiumJS. Aquest projecte mostra en temps real els fluxos de pacients, l'estat dels centres d'atenció primària (CAPs) i hospitals, i les derivacions entre centres.

![Cesium 3D Health Map](https://img.shields.io/badge/CesiumJS-1.107-blue?logo=cesium)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)

## ✨ Característiques

- **Visualització 3D interactiva** amb terreny realista i vista satèl·lit
- **Simulació en temps real** de fluxos de pacients entre centres
- **Representació visual d'ocupació** dels hospitals i CAPs mitjançant cilindres amb codificació de colors
- **Xarxa de connexions** entre centres amb visualització de les rutes d'ambulàncies
- **Panell de control** amb estadístiques en temps real
- **Modes de visualització**:
  - Ambulàncies 3D amb models realistes
  - Partícules de flux per veure patrons de derivació
  - Fluxos civils (llars → CAPs)
- **Vistes de detall** de pacients individuals amb informació clínica
- **Configuració personalitzable** de velocitat de simulació i estils visuals

## 🚀 Demo en Viu

Pots veure la demo en viu aquí: **[https://marcserramasramon.github.io/mapa3d/cesium_proposal/](https://marcserramasramon.github.io/mapa3d/cesium_proposal/)**

## 🛠️ Tecnologies Utilitzades

- [CesiumJS](https://cesium.com/cesiumjs/) - Motor de visualització 3D geoespacial
- JavaScript (ES6+)
- HTML5 + CSS3
- Python (per generals scripts de dades)

## 📋 Prerequisits

Per executar aquest projecte localment necessites:

- Un navegador web modern (Chrome, Firefox, Safari, Edge)
- Un servidor web local (per exemple, Python's `http.server`)
- Token d'accés a Cesium Ion (ja configurat al projecte)

## 🏃 Execució Local

### Opció 1: Utilitzant Python

```bash
# Clona el repositori
git clone https://github.com/marcserramasramon/mapa3d.git
cd mapa3d

# Executa el servidor local
python run_server.py
```

Després obre el navegador a: `http://localhost:8000/cesium_proposal/`

### Opció 2: Utilitzant Node.js (http-server)

```bash
# Instal·la http-server globalment (només la primera vegada)
npm install -g http-server

# Executa el servidor
http-server -p 8000

# Obre http://localhost:8000/cesium_proposal/ al navegador
```

### Opció 3: Utilitzant Extensió de VS Code

Si utilitzes Visual Studio Code, pots usar l'extensió [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) per servir els fitxers directament.

## 📂 Estructura del Projecte

```
mapa3d/
├── cesium_proposal/          # Aplicació principal
│   ├── index.html           # Pàgina principal
│   ├── app.js               # Lògica de l'aplicació
│   ├── style.css            # Estils
│   └── data/
│       └── locations.js     # Dades dels centres sanitaris
├── scripts/                  # Scripts de generació de dades
├── output/                   # Mapes generats amb Python
├── data/                     # Dades de simulació
└── run_server.py            # Servidor HTTP local
```

## 🎮 Controls i Funcionalitats

### Navegació 3D

- **Click esquerre + arrossegar**: Rotar la vista
- **Click dret + arrossegar**: Pan (desplaçar)
- **Roda del ratolí**: Zoom
- **Click sobre un centre**: Mostra informació detallada

### Panell de Configuració

- **Mostrar CAPs / Hospitals**: Activa/desactiva centres
- **Flux de Trànsit**: Mostra/amaga ambulàncies
- **Estil Visual**: Alterna entre ambulàncies 3D i partícules
- **Veure Connexions**: Mostra les rutes aèries entre centres
- **Veure Civils**: Simula fluxos locals cap als CAPs
- **Tipus de Mapa**: Canvia entre vista satèl·lit i OpenStreetMap
- **Velocitat Simulació**: Ajusta la velocitat de la simulació (0.1x - 10x)

### Estadístiques en Temps Real

- **Total Pacients**: Suma de pacients en tots els centres
- **Urgències (1h)**: Taxa d'urgències per hora
- **Ambulàncies Actives**: Número de transferències en curs

## 🎨 Codificació de Colors

### Ocupació dels Centres

- 🟢 **Verd**: < 50% capacitat (situació òptima)
- 🟡 **Groc**: 50-80% capacitat (ocupació moderada)
- 🔴 **Vermell**: > 80% capacitat (sobre capacitat)

### Urgència de Pacients

- Nivell 1 (Verd): Urgència baixa
- Nivell 2-3 (Groc): Urgència moderada
- Nivell 4-5 (Taronja/Vermell): Urgència alta

### Connexions

- 🟡 **Groc**: CAP → Hospital (derivacions primàries)
- 🔵 **Cyan**: Hospital ↔ Hospital (xarxa backbone)

## 📊 Dades de Centres Sanitaris

El projecte inclou dades dels següents centres de la Regió Sanitària de Girona:

### Hospitals

- Hospital Universitari Dr. Josep Trueta (HJT)
- Hospital de Santa Caterina (HSC)
- Hospital de Campdevànol (HCA)
- Hospital de Palamós (HPA)
- Hospital de Figueres (HFI)

### CAPs

- CAP Güell
- CAP Santa Clara
- CAP Montilivi
- I molts més...

## 🔧 Configuració del Token de Cesium

El projecte ja inclou un token d'accés a Cesium Ion. Si necessites el teu propi token:

1. Registra't a [Cesium Ion](https://cesium.com/ion/)
2. Crea un nou token d'accés
3. Substitueix el token a `app.js`:

```javascript
Cesium.Ion.defaultAccessToken = 'EL_TEU_TOKEN_AQUÍ';
```

## 🤝 Contribucions

Les contribucions són benvingudes! Si vols millorar aquest projecte:

1. Fes un fork del repositori
2. Crea una branca per la teva funcionalitat (`git checkout -b feature/nova-funcionalitat`)
3. Commit els teus canvis (`git commit -m 'Afegeix nova funcionalitat'`)
4. Push a la branca (`git push origin feature/nova-funcionalitat`)
5. Obre un Pull Request

## 📝 Llicència

Aquest projecte està llicenciat sota la Llicència MIT - veure el fitxer LICENSE per més detalls.

## 👤 Autor

**Marc Serra Masramon**

- GitHub: [@marcserramasramon](https://github.com/marcserramasramon)

## 🙏 Agraïments

- [CesiumJS](https://cesium.com/) per proporcionar la plataforma de visualització 3D
- Dades dels centres sanitaris de la Regió Sanitària de Girona
- Comunitat de desenvolupadors de CesiumJS

## 📧 Contacte

Si tens preguntes o suggeriments, no dubtis en obrir un issue al repositori!

---

⭐ Si aquest projecte t'ha estat útil, dona-li una estrella!
