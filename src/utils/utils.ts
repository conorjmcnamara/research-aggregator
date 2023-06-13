import Cookies from 'js-cookie'

export function getCookie(name: string) {
    return Cookies.get(name)
}

export interface responseMsgI {
    responseMsg: string;
}

export interface researchPaperI {
    _id: string;
    title: string;
    date: string;
    abstract: string;
    url: string;
    source: string;
    authors: string[];
    topics: string[];
}

export interface researchDataI {
    [_id: string]: researchPaperI
}

export interface showHiddenI {
    [id: string]: boolean
}

interface topicsI {
    [id: string]: string
}

export const topics: topicsI = {
    "AI": "Artificial Intelligence",
    "CL": "Computation and Language",
    "CC": "Computational Complexity",
    "CE": "Computational Engineering, Finance, and Science",
    "CG": "Computational Geometry",
    "CV": "Computer Vision and Pattern Recognition",
    "CY": "Computers and Society",
    "CR": "Cryptography and Security",
    "DS": "Data Structures and Algorithms",
    "DB": "Databases",
    "DL": "Digital Libraries",
    "DM": "Discrete Mathematics",
    "DC": "Distributed, Parallel, and Cluster Computing",
    "ET": "Emerging Technologies",
    "FL": "Formal Languages and Automata Theory",
    "GT": "Game Theory",
    "GR": "Graphics",
    "AR": "Hardware Architecture",
    "HC": "Human-Computer Interaction", 
    "IR": "Information Retrieval",
    "IT": "Information Theory",
    "LO": "Logic in Computer Science",
    "LG": "Machine Learning",
    "MS": "Mathematical Software",
    "MA": "Multiagent Systems",
    "MM": "Multimedia",
    "NI": "Networking and Internet Architecture",
    "NE": "Neural and Evolutionary Computing",
    "NA": "Numerical Analysis",
    "OS": "Operating Systems",
    "PF": "Performance",
    "PL": "Programming Languages",
    "RO": "Robotics",
    "SI": "Social and Information Networks",
    "SE": "Software Engineering",
    "SD": "Sound",
    "SC": "Symbolic Computation",
    "SY": "Systems and Control"
}