from bson.objectid import ObjectId

db_papers_response = [
    {
        "_id": ObjectId("645cfd573007dd700aa1fe7d"),
        "title": "Handwriting Recognition using Artificial Intelligence Neural Network and Image Processing",
        "date": "2023-03-18",
        "abstract": "Due to increased usage of digital technologies in all sectors and in almost all day to day activities to store and pass information, Handwriting character recognition has become a popular subject of research. Handwriting remains relevant, but people still want to have Handwriting copies converted into electronic copies that can be communicated and stored electronically. Handwriting character recognition refers to the computers ability to detect and interpret intelligible Handwriting input from Handwriting sources such as touch screens, photographs, paper documents, and other sources. Handwriting characters remain complex since different individuals have different handwriting styles. This paper aims to report the development of a Handwriting character recognition system that will be used to read students and lectures Handwriting notes. The development is based on an artificial neural network, which is a field of study in artificial intelligence. Different techniques and methods are used to develop a Handwriting character recognition system. However, few of them focus on neural networks. The use of neural networks for recognizing Handwriting characters is more efficient and robust compared with other computing techniques. The paper also outlines the methodology, design, and architecture of the Handwriting character recognition system and testing and results of the system development. The aim is to demonstrate the effectiveness of neural networks for Handwriting character recognition.",
        "url": "https://www.semanticscholar.org/paper/50d12751e65772d81abae6871a9dd5d8c2cfca8e",
        "source": "SemanticScholar.org",
        "authors": ["Sara Aqab", "Muhammad Tariq"],
        "topics": ["AI"]
    },
    {
        "_id": ObjectId("645cfd573007dd700aa1fe80"),
        "title": "IoT-Driven Artificial Intelligence Technique for Fertilizer Recommendation Model",
        "date": "2023-03-01",
        "abstract": "Smart farming systems emphasize the need for modern technologies like the Internet of Things, Cloud, and Artificial Intelligence (AI) in the agricultural process. The digital transformation accelerates conventional farming practices to increase crop production with quality. Earlier works failed to integrate AI with sensor technology, guiding agricultural practitioners in a successful direction. Therefore, we propose an architectural model with four layers, including sensor, network, service, and application, aid in deploying a smart farming system with limited energy consumption. Moreover, focusing on the application layer, we implement a deep learning approach to build a fertilizer recommendation system that matches the experts opinion. Finally, the whole system outcomes are presented as a single mobile application for farmers ease of use.",
        "url": "https://www.semanticscholar.org/paper/04dec21662614458207509ba7389f75838180c5f",
        "source": "SemanticScholar.org",
        "authors": ["B. Swaminathan", "S. Palani", "Subramaniyaswamy Vairavasundaram", "K. Kotecha", "Vinay Kumar"],
        "topics": ["AI"]
    }
]

parsed_db_papers_response = {}
for paper in db_papers_response:
    paper["_id"] = str(paper["_id"])
    parsed_db_papers_response[paper["_id"]] = paper