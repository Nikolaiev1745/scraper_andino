import os
import re
import urllib.parse
import email.utils
from datetime import datetime, timezone, timedelta
import numpy as np
import feedparser
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Librerías de Google Sheets con Service Account
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_formatting import *

# Definición de rutas de credenciales
RUTA_CREDS = os.path.join(os.path.dirname(__file__), "creds.json")
NOMBRE_DOCUMENTO_SHEETS = "Monitoreo Mineria Argentina"

# Parámetros y Semillas
SEMILLAS_POSITIVAS = [
    "extracción de oro", "proyecto de cobre", "lixiviación con cianuro",
    "mina a cielo abierto", "reservas de mineral", "ley de mineral",
    "concesión minera", "planta de procesamiento", "relave",
    "impacto ambiental", "conflicto socioambiental", "declaración de impacto ambiental",
    "exploración avanzada", "Pascua Lama", "Veladero", "Josemaría", "Los Azules",
    "El Pachón", "Gualcamayo", "Barrick", "Yamana", "McEwen Mining",
    "glaciar", "ley de glaciares", "Mike Mending", "Lundin Mining", "BHP", 
    "filo del sol", "José Luis Morea", "Pablo Perea",
    "ley 7722", "ley 5001", "ley XVII 68", "ley 10608", "ley 8229", "ley 7070", 
    "ley 5128", "ley 5772", "decreto 5772", "ley 3753", "fideicomiso UNIR",
    "asamblea de vecinos", "no a la mina", "corte de ruta", "recurso de amparo", 
    "cuenca hidrica", "estudio hidrogeologico", "Fenix", "Salar de Hombre Muerto", 
    "Cauchari-Olaroz", "Tres Quebradas", "Kachi", "Salar de Diablillos", 
    "Proyecto MARA", "Agua Rica", "Bajo de la Alumbrera", "Taca Taca", "Altar", 
    "San Jorge", "COFEMIN", "CAEM"
]

TERMINOS_VAGOS = [
    "minería", "actividad minera", "desarrollo minero", "crecimiento",
    "producción minera", "sector minero", "provincia de San Juan",
    "potencial minero", "trabajo minero", "inversión", "progreso",
    "industria minera", "la minería es", "motor de la economía",
    "récord", "orgullo sanjuanino", "futuro promisorio", "lidera", "polo minero"
]

GLOSARIO_TECNICO = [
    "cobre", "oro", "plata", "molibdeno", "uranio", "litio", "tierras raras",
    "lixiviación", "relave", "cielo abierto", "subterránea", "ley de mineral",
    "reservas", "recurso", "prefactibilidad", "factibilidad", "producción",
    "extracción", "procesamiento", "fundición", "refinación",
    "línea de 500 kv", "campamento", "planta", "concentradora", "ducto",
    "impacto ambiental", "dia", "declaración de impacto", "glaciar",
    "ley de glaciares", "consulta previa", "licencia social",
    "veladero", "josemaría", "los azules", "pachón", "gualcamayo",
    "hualilán", "calcatreu", "vicuña", "barrick", "glencore", "finning",
    "caterpillar", "patagonia gold", "challenger", "mcewen",
    "regalías", "inversión", "capex", "opex", "onzas",
    "rigi", "proveedor minero", "evaluacion de impacto ambiental", "eia", 
    "policia minera", "regalias mineras", "fideicomiso minero", "seguridad juridica",
    "comunidades originarias", "consulta previa", "asamblea legislativa"
]

TERMINOS_NEGATIVOS = [
    "robo de cables", "cables de cobre", "delincuentes", "allanamiento", 
    "detenido", "tendido electrico", "clandestino", "mercado negro", 
    "robado", "sustraccion de cables", "detenidos", "policial"
]

MEDIOS_ANDINOS_Y_ESPECIALIZADOS = [
    "diario de cuyo", "el pregon", "el ancasti", "mining press", "pregon minero", 
    "jujuy al momento", "el tribuno", "mdz online", "mdz", "diario huarpe", "huarpe", 
    "san juan 8", "canal 13 san juan", "tiempo de san juan", "la arena", "el chubut", 
    "la opinion austral", "nuevo dia", "el zonda"
]

PROVINCIAS = ["San Juan", "Mendoza", "Catamarca", "Salta", "Jujuy", "La Rioja", "Santa Cruz", "Chubut", "Neuquen"]
UMBRAL_SCORE_NOTICIAS_VIEJAS = 75.0

def limpiar_texto(texto):
    if not texto: return ""
    texto = texto.lower()
    texto = re.sub(r'[áéíóúü]', lambda m: {'á':'a','é':'e','í':'i','ó':'o','ú':'u','ü':'u'}[m.group(0)], texto)
    texto = re.sub(r'[^a-z0-9ñ\s]', '', texto)
    return texto

def calcular_score_semantico(texto, vectorizer, vec_positivas, vec_vagas):
    txt_limpio = limpiar_texto(texto)
    if not txt_limpio.strip(): return 0.0
    try:
        vec_texto = vectorizer.transform([txt_limpio])
        sim_pos = np.max(cosine_similarity(vec_texto, vec_positivas))
        sim_vaga = np.max(cosine_similarity(vec_texto, vec_vagas))
        score_base = (sim_pos - (sim_vaga * 0.3)) 
        return max(0.0, min(1.0, score_base))
    except:
        return 0.0

def calcular_densidad(texto, glosario):
    txt_limpio = limpiar_texto(texto)
    coincidencias = 0
    for termino in glosario:
        pattern = r'\b' + re.escape(limpiar_texto(termino)) + r'\b'
        coincidencias += len(re.findall(pattern, txt_limpio))
    return coincidencias

def calcular_score_final(texto, medio, vectorizer, vec_positivas, vec_vagas):
    txt_limpio = limpiar_texto(texto)
    for t_neg in TERMINOS_NEGATIVOS:
        if re.search(r'\b' + re.escape(limpiar_texto(t_neg)) + r'\b', txt_limpio):
            return 0.0
            
    score_sem = calcular_score_semantico(texto, vectorizer, vec_positivas, vec_vagas)
    densidad_tecnica = calcular_densidad(texto, GLOSARIO_TECNICO)
    densidad_vaga = calcular_densidad(texto, TERMINOS_VAGOS)
    
    bono_densidad = densidad_tecnica * 0.05 
    score_final = score_sem + bono_densidad
    
    if densidad_vaga > (densidad_tecnica * 2) and densidad_vaga > 2:
        score_final = score_final * 0.6

    score_porcentual = score_final * 100
    medio_limpio = medio.lower().strip()
    if any(m in medio_limpio for m in MEDIOS_ANDINOS_Y_ESPECIALIZADOS):
        score_porcentual += 15.0

    return round(max(1, min(100, score_porcentual)), 2)

def buscar_google_news():
    noticias_captadas = []
    ahora = datetime.now(timezone.utc)
    limite_3_meses = ahora - timedelta(days=90)
    limite_1_ano = ahora - timedelta(days=365)
    
    corpus_entrenamiento = [limpiar_texto(t) for t in SEMILLAS_POSITIVAS + TERMINOS_VAGOS]
    vectorizer = TfidfVectorizer().fit(corpus_entrenamiento)
    vec_positivas = vectorizer.transform([limpiar_texto(t) for t in SEMILLAS_POSITIVAS])
    vec_vagas = vectorizer.transform([limpiar_texto(t) for t in TERMINOS_VAGOS])

    for prov in PROVINCIAS:
        query = f"mineria {prov} o cobre o litio"
        query_encoded = urllib.parse.quote(query)
        url_rss = f"https://news.google.com/rss/search?q={query_encoded}&hl=es-AR&gl=AR&ceid=AR:es"
        
        feed = feedparser.parse(url_rss)
        print(f"Escaneando {prov}... Procesando {len(feed.entries)} entradas.")
        
        for entry in feed.entries:
            try:
                fecha_publicacion = email.utils.parsedate_to_datetime(entry.published)
            except:
                fecha_publicacion = ahora

            if fecha_publicacion < limite_1_ano:
                continue
                
            titulo = entry.title
            medio = "Desconocido"
            if " - " in titulo:
                partes = titulo.split(" - ")
                medio = partes[-1].strip()
                titulo = " - ".join(partes[:-1]).strip()
                
            url = entry.link
            resumen = entry.summary if 'summary' in entry else ""
            resumen_limpio = re.sub('<[^<]+?>', '', resumen).strip()
            texto_completo = f"{titulo} {resumen_limpio}"
            
            autor = ""
            if 'author' in entry and entry.author.strip():
                autor = entry.author.strip()
            elif 'authors' in entry and entry.authors:
                autor = ", ".join([a.name for a in entry.authors if 'name' in a])
                
            if not autor:
                autor = f"Redacción de {medio}"
            
            score = calcular_score_final(texto_completo, medio, vectorizer, vec_positivas, vec_vagas)
            if score == 0.0:
                continue
                
            if fecha_publicacion < limite_3_meses:
                if score < UMBRAL_SCORE_NOTICIAS_VIEJAS:
                    continue 

            fecha_espanol = fecha_publicacion.strftime('%d/%m/%Y')

            if not any(n['url'] == url for n in noticias_captadas):
                noticias_captadas.append({
                    'titulo': titulo,
                    'fecha': fecha_espanol,
                    'medio': medio,
                    'autor': autor,
                    'descripcion': resumen_limpio,
                    'url': url,
                    'score': score
                })
                
    return noticias_captadas

def guardar_en_sheets(noticias):
    if not os.path.exists(RUTA_CREDS):
        print(f"[Error] No se encontró 'creds.json' en {RUTA_CREDS}.")
        return

    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(RUTA_CREDS, scope)
    gc = gspread.authorize(creds)

    try:
        sh = gc.open(NOMBRE_DOCUMENTO_SHEETS)
        ws = sh.get_worksheet(0)
    except gspread.exceptions.SpreadsheetNotFound:
        sh = gc.create(NOMBRE_DOCUMENTO_SHEETS)
        ws = sh.get_worksheet(0)
        
    ws.clear()
    
    cabeceras = ["titulo", "fecha", "medio", "autor", "descripcion", "url (fuente)", "score de precision"]
    ws.append_row(cabeceras)
    
    noticias_ordenadas = sorted(noticias, key=lambda x: x['score'], reverse=True)
    filas_a_guardar = []
    for n in noticias_ordenadas:
        filas_a_guardar.append([n['titulo'], n['fecha'], n['medio'], n['autor'], n['descripcion'], n['url'], n['score']])
        
    if filas_a_guardar:
        ws.append_rows(filas_a_guardar)
        total_filas = len(filas_a_guardar) + 1
        rango_score = f"G2:G{total_filas}"
        
        regla_gradiente = ConditionalFormatRule(
            ranges=[GridRange.from_a1_range(rango_score, ws)],
            gradientRule=GradientRule(
                minpoint=InterpolationPoint(color=Color(1, 1, 1), type='NUMBER', value='1'),
                midpoint=InterpolationPoint(color=Color(0.78, 0.93, 0.80), type='NUMBER', value='50'),
                maxpoint=InterpolationPoint(color=Color(0.10, 0.36, 0.12), type='NUMBER', value='100')
            )
        )
        
        rules = get_conditional_format_rules(ws)
        rules.clear() 
        rules.append(regla_gradiente)
        rules.save()
        
        set_data_validation_for_cell_range(ws, rango_score, None)
        print(f"✓ ¡Base de datos actualizada! Planilla: {sh.url}")

if __name__ == "__main__":
    print("Iniciando escáner...")
    listado = buscar_google_news()
    guardar_en_sheets(listado)
