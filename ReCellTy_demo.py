import os
from langchain_neo4j import Neo4jGraph
from Agents.name_joint import ReCellTy
from langchain.chat_models import init_chat_model

# Define Neo4j credentials
os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "your_password"

graph = Neo4jGraph()

os.environ["OPENAI_API_KEY"] = 'your_api_key'
model = init_chat_model('gpt-4o', model_provider="openai", temperature=0)

top_different_genes = 'MS4A1, TNFRSF13B, IGHM, IGHD, AIM2, CD79A, LINC01857, RALGPS2, BANK1, CD79B'


# Select tissue_class from the following tissues
tissue_class_options = [
    'Amniotic fluid', 'Fetus', 'Eye', 'Spinal cord', 'Ovary', 'Cavernosum',
    'Umbilical cord', 'Cerebral organoid', 'Ligament', 'Cornea', 'Fetal striatum',
    'Tendon', 'Placenta', 'Epithelium', 'Skeletal muscle', 'Respiratory tract', 'Uterus',
    'Testis', 'Mammary gland', 'Embryo', 'Brain', 'Neck', 'Biliary tract', 'Epidermis',
    'Nasal', 'Sinus tissue', 'Blood vessel', 'Nerve', 'Undefined', 'Synovium', 'Gall bladder',
    'Peritoneal fluid', 'Bone marrow', 'Nasopharynx', 'Taste bud', 'Synovial fluid', 'Tonsil',
    'Colon', 'Tongue', 'Trachea', 'Bile duct', 'Peritoneum', 'Gingiva', 'Artery', 'Spleen',
    'Intervertebral disc', 'Gonad', 'Fetal brain', 'Ascites', 'Liver', 'Kidney', 'Stomach',
    'Inferior colliculus', 'Pharynx', 'Scalp', 'Pancreas', 'Lymph node', 'Tooth', 'Salivary gland',
    'Oral cavity', 'Pleura', 'Meniscus', 'Gut', 'Head and neck', 'Heart', 'Esophagus', 'Decidua',
    'Palatine tonsil', 'Head', 'Abdomen', 'Periodontium', 'Thyroid', 'Bone', 'Belly', 'Intestine',
    'Adipose tissue', 'Adventitia', 'Sputum', 'Soft tissue', 'Cervix', 'Prostate', 'Esophageal',
    'Joint', 'Nodular tissue', 'Cartilage', 'Genitals', 'Articulation', 'Vein', 'Suprarenal gland',
    'Bronchus', 'Fetal liver', 'Muscle', 'Thorax', 'Endocrine organ', 'Airway', 'Airway epithelium',
    'Synovial', 'Adrenal gland', 'Bladder', 'Articular\xa0Cartilage', 'Endometrium', 'Uterine cervix',
    'Skin', 'Germ', 'Thymus', 'Breast', 'Lymph', 'Limb', 'Knee', 'Lymphoid tissue', 'Blood', 'Arthrosis',
    'Oviduct', 'Periosteum', 'Bronchi', 'Lung', 'Urine', 'Vagina', 'Larynx', 'Fundic gland', 'Nose',
    'Gastrointestinal tract', 'Knee joint']

tissue_class = 'Blood'
tissue_type = 'PBMC'

cell_type, broad_cell_type, marker_feature, feature = ReCellTy(graph, top_different_genes, model, tissue_class, tissue_type)

print('Cell Type annotation results are as follows:')
print('**************************************************')
print(f"Cell Type: {cell_type}")
print('**************************************************')
print(f"Broad Cell Type: {broad_cell_type}")
print('**************************************************')
print(f"Marker Features: {marker_feature}")
print('**************************************************')
print(f"Features: {feature}")
print('**************************************************')