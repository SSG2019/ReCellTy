import os
import time
import asyncio
import threading
import tkinter as tk
from PIL import ImageGrab, Image
from tkinter import ttk, messagebox
from langchain_neo4j import Neo4jGraph
from langchain_openai import ChatOpenAI
from Agents.name_joint import celltypeQA
from langchain.chat_models import init_chat_model
from Agents.cell_type_broad import broad_type_agent, bct_judgement
from Agents.cell_type_sub import sub_type_agent, feature_select, segment_output

os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "your_password"

marker_graph = Neo4jGraph()

info_tissue_type = {
    'global_research':[],
    'Amniotic fluid': ['Amniotic fluid'],
    'Fetus': ['Fetus', 'Heart'],
    'Eye': ['Cornea', 'Choroid', 'Retinal organoid', 'Corneal endothelium', 'Limbal epithelium', 'Retina', 'Retinal pigment epithelium', 'Lacrimal gland', 'Eye', 'Blood', 'Artery', 'Choriocapillaris', 'Sclerocorneal tissue', 'Corneal epithelium'],
    'Spinal cord': ['Spinal cord'],
    'Ovary': ['Corpus luteum', 'Ovary', 'Oviduct', 'Uterus', 'Myometrium', 'Ovarian cortex', 'Vagina', 'Omentum', 'Ovarian follicle'],
    'Cavernosum': ['Cavernosum'],
    'Umbilical cord': ['Umbilical cord blood', 'Whartons jelly', 'Umbilical cord'],
    'Cerebral organoid': ['Diencephalon', 'Cerebral organoid'],
    'Ligament': ['Anterior cruciate ligament', 'Ligament'],
    'Cornea': ['Cornea'], 'Fetal striatum': ['Lateral ganglionic eminence'],
    'Tendon': ['Tendon'],
    'Placenta': ['Chorionic villi', 'Amniotic membrane', 'Chorionic villus', 'Placenta', 'Amniotic fluid'],
    'Epithelium': ['Airway epithelium', 'Mammary epithelium', 'Epithelium'],
    'Skeletal muscle': ['Skeletal muscle'],
    'Respiratory tract': ['Respiratory tract'],
    'Uterus': ['Endometrium', 'Uterus', 'Endometrium stroma', 'Decidua', 'Myometrium', 'Ectocervix'],
    'Testis': ['Sperm', 'Seminal plasma', 'Testis'], 'Mammary gland': ['Mammary gland'],
    'Embryo': ['Transformed artery', 'Posterior presomitic mesoderm', 'Cornea', 'Cortex', 'Caudal cortex', 'Testis', 'Limb bud', 'Embryonic brain', 'Presomitic mesoderm', 'Fetal kidney', 'Subplate', 'Trophoblast', 'Endoderm', 'Embryoid body', 'Vein', 'Frontal cortex', 'Anterior presomitic mesoderm', 'Embryo', 'Fetal ileums', 'Fetal Leydig', 'Muscle', 'Skeletal muscle', 'Calvaria', 'Embryonic stem cell', 'Mesoderm', 'Ectoderm', 'Endometrium', 'Primitive streak', 'Embryonic prefrontal cortex', 'Skin', 'Fetal umbilical cord', 'Blood vessel', 'Umbilical cord', 'Embryonic heart', 'Liver'],
    'Brain': ['Frontal cortex', 'Dorsolateral prefrontal cortex', 'Superior frontal gyrus', 'Central amygdala', 'Cerebellum', 'Pituitary gland', 'Nerve', 'Pluripotent stem cell', 'Caudal ganglionic eminence', 'Hippocampus', 'Cortical layer', 'Vessel', 'Dorsal forebrain', 'Ventral thalamus', 'Middle temporal gyrus', 'Posterior fossa', 'Medial ganglionic eminence', 'Microvascular endothelium', 'Cerebrospinal fluid', 'Fetal brain', 'Epithelium', 'Cortex', 'Thalamus', 'Prefrontal cortex', 'Midbrain', 'Allocortex', 'Central nervous system', 'White matter', 'Choroid plexus', 'Entorhinal cortex', 'Brain', 'Pituitary', 'Auditory cortex', 'Blood vessel', 'Neocortex', 'Caudal forebrain', 'Corpus callosum'],
    'Neck': ['Neck', 'Vocal cord'],
    'Biliary tract': ['Biliary tract'],
    'Epidermis': ['Epidermis'],
    'Nasal': ['Nasal mucosa'],
    'Sinus tissue': ['Sinus tissue'],
    'Blood vessel': ['Blood vessel', 'Artery', 'Capillary', 'Carotid plaque', 'Carotid artery', 'Microvessel'],
    'Nerve': ['Optic nerve', 'Nerve', 'Sympathetic ganglion'],
    'Undefined': ['Pluripotent stem cell', 'Undefined'],
    'Synovium': ['Synovium'], 'Gall bladder': ['Gall bladder'],
    'Peritoneal fluid': ['Peritoneal fluid'],
    'Bone marrow': ['Synovium', 'Bone marrow', 'Spinal cord', 'Dorsal root ganglion', 'Nucleus pulposus'],
    'Nasopharynx': ['Nasopharyngeal mucosa', 'Nasopharynx', 'Epithelium'],
    'Taste bud': ['Taste bud'],
    'Synovial fluid': ['Synovial fluid'],
    'Tonsil': ['Tonsil', 'Palatine tonsil'],
    'Colon': ['Colon'],
    'Tongue': ['Tongue'],
    'Trachea': ['Epithelium', 'Trachea', 'Bronchiole'],
    'Bile duct': ['Bile duct'],
    'Peritoneum': ['Peritoneum'],
    'Gingiva': ['Gingiva'],
    'Artery': ['Aorta', 'Coronary artery', 'Aortic valve', 'Artery'],
    'Spleen': ['Splenic red pulp', 'Spleen'],
    'Intervertebral disc': ['Nucleus pulposus', 'Intervertebral disc'],
    'Gonad': ['Gonad', 'Fetal gonad'],
    'Fetal brain': ['Ventricular zone', 'Lateral ganglionic eminence', 'Subventricular zone', 'Subpallium'],
    'Ascites': ['Ascites'],
    'Liver': ['Fetal liver', 'Biliary tract', 'Lymphatic vessel', 'Bile duct', 'Blood vessel', 'Intrahepatic cholangio', 'Ductal tissue', 'Liver', 'Left lobe'],
    'Kidney': ['Embryonic Kidney', 'Artery', 'Kidney', 'Renal glomerulus', 'Lymphoid tissue', 'Adrenal gland', 'Prostate', 'Epithelium', 'Fetal kidney'],
    'Stomach': ['Epithelium', 'Gastric epithelium', 'Gastric corpus', 'Gastric gland', 'Pyloric gland', 'Stomach'],
    'Inferior colliculus': ['Inferior colliculus'], 'Pharynx': ['Nasopharynx'],
    'Scalp': ['Scalp'],
    'Pancreas': ['Endocrine', 'Pancreas', 'Fetal pancreas', 'Acinus', 'Pancreatic acinar tissue', 'Vein', 'Pancreatic duct', 'Pancreatic islet'],
    'Lymph node': ['Lymph node', 'Lymphoid tissue', 'Lymph'],
    'Tooth': ['Duodenum', 'Tooth', 'Periodontal ligament', 'Premolar', 'Molar', 'Deciduous tooth', 'Dental pulp'],
    'Salivary gland': ['Saliva', 'Epithelium', 'Salivary gland', 'Submandibular gland', 'Parotid gland'],
    'Oral cavity': ['Oral mucosa', 'Oral cavity'],
    'Pleura': ['Pleura'],
    'Meniscus': ['Meniscus'],
    'Gut': ['Gut'],
    'Head and neck': ['Head and neck'],
    'Heart': ['Ventricular and atrial', 'Aorta', 'Ventricle', 'Embryonic heart', 'Endocardium', 'Myocardium', 'Heart muscle', 'Right ventricle', 'Mesoblast', 'Vein', 'Heart', 'Cardiovascular system', 'Central nervous system', 'Fetal heart', 'Atrium', 'Cardiac atrium', 'Blood', 'Blood vessel', 'Artery'],
    'Esophagus': ['Esophagus'],
    'Decidua': ['Decidua'],
    'Palatine tonsil': ['Germinal center'],
    'Head': ['Head'],
    'Abdomen': ['Abdominal fat pad', 'Abdomen'],
    'Periodontium': ['Periodontium', 'Periodontal ligament'],
    'Thyroid': ['Thyroid'],
    'Bone': ['Spinal cord', 'Meniscus', 'Synovial fluid', 'Cartilage', 'Synovium', 'Iliac crest', 'Lumbar vertebra', 'Bone'],
    'Belly': ['Ampullary', 'Ascitic fluid', 'Ascites'],
    'Intestine': ['Intestinal crypt', 'Duodenum', 'Large intestine', 'Colon', 'Gastrointestinal tract', 'Colorectum', 'Colon epithelium', 'Gut', 'Intestine', 'Ileum', 'Lymph node', 'Small intestine', 'Epithelium', 'Small intestinal crypt', 'Myenteric plexus', 'Large Intestine', 'Rectum', 'Jejunum'],
    'Adipose tissue': ['Subcutaneous adipose tissue', 'Fat pad', 'Lymph', 'Brown adipose tissue', 'Beige Fat', 'Adipose tissue', 'White adipose tissue', 'Visceral adipose tissue', 'Abdominal adipose tissue'],
    'Adventitia': ['Adventitia'],
    'Sputum': ['Sputum'],
    'Soft tissue': ['Soft tissue'],
    'Cervix': ['Cervix'],
    'Prostate': ['Epithelium', 'Prostate', 'Epidermis', 'Basilar membrane'],
    'Esophageal': ['Esophageal'],
    'Joint': ['Synovium', 'Synovial fluid'],
    'Nodular tissue': ['Blood vessel'],
    'Cartilage': ['Cartilage', 'Osteoarthritic cartilage'],
    'Genitals': ['Anogenital tract'],
    'Articulation': ['Synovium'],
    'Vein': ['Antecubital vein', 'Vein', 'Umbilical vein'],
    'Suprarenal gland': ['Adrenal gland'],
    'Bronchus': ['Bronchoalveolar system'],
    'Fetal liver': ['Yolk sac'],
    'Muscle': ['Septum transversum', 'Skeletal muscle', 'Muscle'],
    'Thorax': ['Malignant pleural effusion'],
    'Endocrine organ': ['Pituitary gland'],
    'Airway': ['Airway', 'Bronchus', 'Epithelium'],
    'Airway epithelium': ['Distal airway'],
    'Synovial': ['Synovium'],
    'Adrenal gland': ['Adrenal gland'],
    'Bladder': ['Bladder', 'Urothelium'],
    'Articular\xa0Cartilage': ['Articular\xa0Cartilage'],
    'Endometrium': ['Endometrium'],
    'Uterine cervix': ['Uterine cervix'],
    'Skin': ['Epithelium', 'Hair follicle', 'Dermis', 'Lymphoid tissue', 'Scalp', 'Interfollicular epidermis', 'Subcutaneous adipose tissue', 'Epidermis', 'Foreskin', 'Skin'],
    'Germ': ['Germ'],
    'Thymus': ['Thymus', 'Blood vessel', 'Fetal thymus', 'Medullary thymus', 'Cortical thymus', 'Epithelium'],
    'Breast': ['Mammary gland', 'Muscle', 'Breast', 'Mesenchyme', 'Milk', 'Epithelium', 'Blood', 'Skin', 'Thymus', 'Fat pad'],
    'Lymph': ['Lymph', 'Lymphatic vessel'],
    'Limb': ['Skin'],
    'Knee': ['Synovial fluid'],
    'Lymphoid tissue': ['Lymphoid tissue', 'Lymph node'],
    'Blood': ['Plasma', 'Serum exosome', 'Blood', 'Peripheral blood', 'Serum', 'Venous blood', 'Sputum', 'Umbilical cord blood', 'Lymph'],
    'Arthrosis': ['Arthrosis'],
    'Oviduct': ['Oviduct'],
    'Periosteum': ['Periosteum'],
    'Bronchi': ['Epithelium'],
    'Lung': ['Bronchiole', 'Bronchoalveolar lavage', 'Pulmonary arteriy', 'Bronchoalveolar system', 'Alveolus', 'Bronchial vessel', 'Vein', 'Capillary', 'Airway', 'Fetal lung', 'Lung', 'Artery', 'Bronchus', 'Basal airway', 'Lymph', 'Epithelium'],
    'Urine': ['Urine'],
    'Vagina': ['Vagina'],
    'Larynx': ['Laryngeal squamous epithelium', 'Larynx', 'Vocal fold'],
    'Fundic gland': ['Fundic gland'],
    'Nose': ['Nasal polyp', 'Nasal mucosa', 'Tracheal airway epithelium', 'Polyp', 'Sinonasal mucosa', 'Nasal concha', 'Olfactory neuroepithelium', 'Nose', 'Nasal epithelium'],
    'Gastrointestinal tract': ['Esophagus', 'Gastrointestinal tract', 'Stomach'], 'Knee joint': ['Synovium']
}

info_tissue_class = list(info_tissue_type.keys())

def select_model(model, api_key, api_base):
    if str(model) == "gpt-4o-mini":
        os.environ["OPENAI_API_KEY"] = str(api_key)
        selected_model = init_chat_model('gpt-4o-mini', model_provider="openai", temperature=0, base_url=str(api_base))
    elif str(model) == "gpt-4o":
        os.environ["OPENAI_API_KEY"] = str(api_key)
        selected_model = init_chat_model('gpt-4o', model_provider="openai", temperature=0, base_url=str(api_base))
    elif str(model) == "deepseek-chat":
        os.environ["OPENAI_API_KEY"] = str(api_key)
        # os.environ["OPENAI_API_BASE"] = 'https://api.deepseek.com/v1'
        # selected_model = ChatOpenAI(model='deepseek-chat', temperature=0)
        selected_model = init_chat_model('deepseek-chat', model_provider="openai", temperature=0, base_url='https://api.deepseek.com/v1')
    elif str(model) == 'claude-3-7':
        os.environ["ANTHROPIC_API_KEY"] = str(api_key)
        selected_model = init_chat_model('claude-3-7-sonnet-20250219', model_provider="anthropic", temperature=0,
                                base_url=str(api_base))
    else:
        selected_model = None
    return selected_model

def run_cell_annotation(model, api_key, api_base, tissue_class, tissue_type, markers):
    try:
        progress_bar.start(10)

        selected_model = select_model(model, api_key, api_base)

        if tissue_class == 'global_research':
            global_search = True
        else:
            global_search = False

        output_text.insert(tk.END, "[INFO] Annotating broad cell type\n")
        broad_cell_type_info = broad_type_agent(selected_model, marker_graph, markers, tissue_class, global_search=global_search)
        broad_cell_type = bct_judgement(selected_model, broad_cell_type_info, tissue_type)
        output1_text.insert(tk.END, broad_cell_type)

        output_text.insert(tk.END, "[INFO] Querying related features and functions\n")
        marker_feature = sub_type_agent(selected_model, marker_graph, markers, tissue_class, global_search=global_search)
        output2_text.insert(tk.END, marker_feature)

        output_text.insert(tk.END, "[INFO] Narrowing the features and functions scope\n")
        x = feature_select(selected_model, broad_cell_type, marker_feature)
        try:
            feature = segment_output(x)
        except:
            feature = 'NA'
        output3_text.insert(tk.END, feature)

        output_text.insert(tk.END, "[INFO] Performing the final annotation\n")
        cell_type = celltypeQA(selected_model, markers, broad_cell_type, feature)
        output4_text.insert(tk.END, cell_type)

        output_text.insert(tk.END, "[INFO] Annotation completed\n")
        progress_bar.stop()


    except Exception as e:
        progress_bar.stop()

        messagebox.showerror("Error", f"An error occurred: {str(e)}")


def save_as_pdf():
    root.update()
    time.sleep(0.1)
    x = root.winfo_rootx()
    y = root.winfo_rooty()
    width = root.winfo_width()
    height = root.winfo_height()
    img = ImageGrab.grab(bbox=(x, y, x + width, y + height))

    img = img.resize((img.width * 5, img.height * 5), Image.Resampling.LANCZOS)

    img.save("screenshot.pdf", "PDF")
    print("PDF saved!")

# def run_analysis():
#     if not model_var.get() or not tissue_entry.get() or not genes_entry.get():
#         messagebox.showwarning("输入错误", "请填写所有输入项！")
#         return
#
#     threading.Thread(target=run_cell_annotation).start()

def run_analysis():
    # save_as_pdf()
    model = model_var.get()
    api_key = api_entry.get()
    api_base = api_base_entry.get()
    tissue_class = model_var_tissue_class.get()
    tissue_type = model_var_tissue_type.get()
    markers = genes_entry.get()

    if not api_key:
        messagebox.showwarning("Input Error", "Please enter the api key!")
        return
    if not markers:
        messagebox.showwarning("Input Error", "Please enter differential marker genes!")
        return

    output_text.delete(1.0, tk.END)
    output1_text.delete(1.0, tk.END)
    output2_text.delete(1.0, tk.END)
    output3_text.delete(1.0, tk.END)
    output4_text.delete(1.0, tk.END)

    threading.Thread(target=lambda: run_cell_annotation(model, api_key, api_base, tissue_class, tissue_type, markers)).start()

    # start_loading_animation()

    # thread = threading.Thread(target=lambda: [
    #     run_cell_annotation(model, api_key, tissue, genes, output_text),
    #     stop_loading_animation()
    # ])
    # thread.start()




# def start_loading_animation():
#     global is_loading
#     is_loading = True
#     update_loading_animation()
#
# def stop_loading_animation():
#     global is_loading, loading_canvas
#     is_loading = False
#     if loading_canvas:
#         loading_canvas.delete("all")
#
# def update_loading_animation():
#     global rotation_angle, loading_canvas
#     if is_loading and loading_canvas:
#         loading_canvas.delete("all")
#         loading_canvas.create_arc(5, 5, 30, 30, start=rotation_angle, extent=60, style=tk.ARC, width=3)
#         rotation_angle = (rotation_angle + 20) % 360
#         root.after(50, update_loading_animation)



def update_options(event):
    selected = model_var_tissue_class.get()

    if selected in info_tissue_type and len(info_tissue_type[selected]) > 0:
        model_dropdown2['values'] = info_tissue_type[selected]
        model_dropdown2.current(0)
    else:
        model_dropdown2['values'] = []
        model_dropdown2.set('')

root = tk.Tk()
root.title("ReCellTy v1.1")
root.iconbitmap("data/graph.ico")
root.geometry("620x400")

style = ttk.Style()
style.configure("TButton", font=("Arial", 10), padding=6)
style.configure("TLabelFrame", font=("Arial", 10, "bold"))
style.configure("TEntry", padding=5)

frame_inputs1 = ttk.LabelFrame(root, text="Select Model", padding=(10, 5))
frame_inputs1.place(x=10, y=10, width=280, height=128)


tk.Label(root, text="Model:").place(x=20, y=35)
model_var = tk.StringVar()
model_dropdown = ttk.Combobox(root, textvariable=model_var, values=["gpt-4o-mini", "gpt-4o", "deepseek-chat", 'claude-3-7'])
model_dropdown.place(x=110, y=35, width=145)
model_dropdown.current(0)

# API Key
tk.Label(root, text="API Key:").place(x=20, y=70)
api_entry = tk.Entry(root, show="*")
api_entry.place(x=110, y=70)
# API Base
tk.Label(root, text="API Base:").place(x=20, y=105)
api_base_entry = tk.Entry(root, show="*")
api_base_entry.place(x=110, y=105)


frame_inputs1 = ttk.LabelFrame(root, text="Input Parameter", padding=(10, 5))
frame_inputs1.place(x=10, y=140, width=280, height=160)

tk.Label(root, text="TissueClass:").place(x=20, y=165)
# frame_inputs2 = ttk.LabelFrame(root, text="Input Parameter", padding=(10, 5))
model_var_tissue_class = tk.StringVar()
model_dropdown1 = ttk.Combobox(root, textvariable=model_var_tissue_class, values=info_tissue_class)
model_dropdown1.bind("<<ComboboxSelected>>", update_options)
model_dropdown1.place(x=110, y=165, width=120, height=20)

tk.Label(root, text="TissueType:").place(x=20, y=195)
model_var_tissue_type = tk.StringVar()
model_dropdown2 = ttk.Combobox(root, textvariable=model_var_tissue_type)
model_dropdown2.place(x=110, y=195, width=120, height=20)
# update_options(None)


# tk.Label(root, text="Tissue:").place(x=20, y=145)
# tissue_entry = tk.Entry(root)
# tissue_entry.place(x=120, y=145)


tk.Label(root, text="Marker:").place(x=20, y=225)
genes_entry = tk.Entry(root)
genes_entry.place(x=110, y=225)


# style = ttk.Style()
# style.configure(
#     "Decor.TFrame",
#     background="#ffffff",
#     borderwidth=2,
#     relief="solid",
#     bordercolor="#34495e"
# )
# decor_frame = ttk.Frame(root, style="Decor.TFrame", padding=10)
# decor_frame.place(x=40, y=213, width=200, height=50)

tk.Button(root, text="Run", command=run_analysis, width=5, height=1).place(x=50, y=260)


progress_bar = ttk.Progressbar(root, mode="indeterminate", length=140)
progress_bar.place(x=130, y=265, width=100, height=20)


tk.Label(root, text="Processing Phase:").place(x=10, y=305)
output_text = tk.Text(root, height=5, width=39, state=tk.NORMAL)
output_text.bind("<Key>", lambda e: "break")
output_text.place(x=10, y=325)



frame_inputs3 = ttk.LabelFrame(root, text="Output Information", padding=(10, 5))
frame_inputs3.place(x=300, y=10, width=310, height=384)
# output
tk.Label(root, text="Broad Type:").place(x=310, y=35)
output1_text = tk.Text(root, height=2.5, width=40, state=tk.NORMAL)
output1_text.bind("<Key>", lambda e: "break")
output1_text.place(x=310, y=55)

tk.Label(root, text="Relevant Features:").place(x=310, y=105)
output2_text = tk.Text(root, height=7.5, width=40, state=tk.NORMAL)
output2_text.bind("<Key>", lambda e: "break")
output2_text.place(x=310, y=125)

tk.Label(root, text="Selected Features:").place(x=310, y=244)
output3_text = tk.Text(root, height=2.5, width=40, state=tk.NORMAL)
output3_text.bind("<Key>", lambda e: "break")
output3_text.place(x=310, y=264)

tk.Label(root, text="Cell Type Annotation:").place(x=310, y=314)
output4_text = tk.Text(root, height=2.5, width=40, state=tk.NORMAL)
output4_text.bind("<Key>", lambda e: "break")
output4_text.place(x=310, y=334)

root.mainloop()
