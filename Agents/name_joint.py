from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from langchain_openai import ChatOpenAI
from Agents.cell_type_broad import broad_type_agent, bct_judgement
from Agents.cell_type_sub import sub_type_agent, feature_select, segment_output

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


system_prompt = """
You are an intelligent assistant tasked with annotating cell types. 
Given the determined broad cell type and the associated features and functions, determine the most likely cell type.
"""

task_prompt = """
Given the following information:
marker: {marker}
broad cell type: {broad_cell}
feature&function: {feature_function}

Return only the cell type as the output.
"""

def celltypeQA(model, marker, cell_broad, feature):

    celltypeqa_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", task_prompt),
    ])
    celltypeqa_chain =  celltypeqa_prompt | model | StrOutputParser()

    input_data = {
        "marker": marker,
        "broad_cell": cell_broad,
        "feature_function": feature,
    }

    response = celltypeqa_chain.invoke(input_data)
    return response

def search_model(num, your_api_key):
    if num == 0:
        os.environ["OPENAI_API_KEY"] = your_api_key
        model = ChatOpenAI(model='gpt-4o-mini-2024-07-18', temperature=0)
    elif num == 1:
        os.environ["OPENAI_API_KEY"] = your_api_key
        model = ChatOpenAI(model='gpt-4o-2024-11-20', temperature=0)
    elif num == 2:
         os.environ["OPENAI_API_KEY"] = your_api_key
         model = ChatOpenAI(model='gpt-4', temperature=0)
    elif num == 3:
        os.environ["OPENAI_API_KEY"] = your_api_key
        os.environ["OPENAI_API_BASE"] = 'https://api.deepseek.com'
        model = ChatOpenAI(model='deepseek-chat', temperature=0)
    else:
        model = None
    return model


def cell_type_qa(marker_graph, markers, model, tissue_class, tissue_type, global_search=False):
    broad_cell_type_info = broad_type_agent(model, marker_graph, markers, tissue_class, global_search=global_search)
    broad_cell_type = bct_judgement(model, broad_cell_type_info, tissue_type)
    marker_feature = sub_type_agent(model, marker_graph, markers, tissue_class, global_search=global_search)
    x = feature_select(model, broad_cell_type, marker_feature)
    try:
        feature = segment_output(x)
    except:
        feature = 'NA'
    cell_type = celltypeQA(model, markers, broad_cell_type, feature)
    return cell_type, broad_cell_type, marker_feature, feature

def ReCellTy(marker_graph, markers, model, tissue_class, tissue_type, global_search=False):
    """
    :param marker_graph: pass the graph database to the function
    :param markers: top differentially expressed genes
    :param model: Select the model to use
    :param tissue_class: this parameter is used to narrow the scope of the map retrieval, please make a selection.
    :param tissue_type: this parameter is used to assist the model in making judgments.
    :param global_search: enable global graph dataset retrieval, i.e., ignore 'tissue_class'
    :return: return in order: final annotation type, cell major category, all relevant features, filtered features.
    """

    if not global_search:
        if tissue_class not in tissue_class_options:
            raise ValueError(f"Invalid tissue_class: {tissue_class}")

    broad_cell_type_info = broad_type_agent(model, marker_graph, markers, tissue_class, global_search=global_search)
    broad_cell_type = bct_judgement(model, broad_cell_type_info, tissue_type)
    marker_feature = sub_type_agent(model, marker_graph, markers, tissue_class, global_search=global_search)
    x = feature_select(model, broad_cell_type, marker_feature)
    try:
        feature = segment_output(x)
    except:
        feature = 'NA'
    cell_type = celltypeQA(model, markers, broad_cell_type, feature)
    return cell_type, broad_cell_type, marker_feature, feature
