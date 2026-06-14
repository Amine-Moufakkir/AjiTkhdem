--- Prompt 7 Test Results (Fixed) ---
GET /api/jobs:
{
  "jobs": [
    {
      "id": "job-1",
      "title": "Lead Fullstack Practitioner (M/F)",
      "company": "Vortex Analytics",
      "location": "Paris",
      "workModel": "Hybrid",
      "salaryMin": 100.0,
      "salaryMax": 120.0,
      "type": "Full-time",
      "description": "FTS matched desc... Python and React Developer",
      "requirements": [],
      "match": {
        "jobId": null,
        "score": 72,
        "reasons": null
      },
      "applied": false,
      "applicationStatus": null
    },
    {
      "id": "job-2",
      "title": "Python Data Scientist",
      "company": "Vortex Analytics",
      "location": "Remote",
      "workModel": "Hybrid",
      "salaryMin": 120.0,
      "salaryMax": 144.0,
      "type": "Full-time",
      "description": "Looking for Python expert",
      "requirements": [],
      "match": {
        "jobId": null,
        "score": 50,
        "reasons": null
      },
      "applied": false,
      "applicationStatus": null
    }
  ]
}

POST /api/recommendations (Python):
{
  "jobs": [
    {
      "id": "job-1",
      "title": "Lead Fullstack Practitioner (M/F)",
      "company": "Vortex Analytics",
      "location": "Paris",
      "workModel": "Hybrid",
      "salaryMin": 100.0,
      "salaryMax": 120.0,
      "type": "Full-time",
      "description": "FTS matched desc... Python and React Developer",
      "requirements": [
        "Python",
        "SQL"
      ],
      "match": {
        "jobId": "job-1",
        "score": 91,
        "reasons": {
          "skills": "Votre profil de Python correspond idéalement aux compétences demandées pour ce poste de Lead Fullstack Practitioner (M/F).",
          "location": "Le statut hybride répond parfaitement à vos critères.",
          "salary": "Votre attente salariale est en phase avec la grille de l'entreprise.",
          "jobType": "Le poste cadre avec vos projets professionnels."
        }
      },
      "applied": false,
      "applicationStatus": null
    },
    {
      "id": "job-2",
      "title": "Python Data Scientist",
      "company": "Vortex Analytics",
      "location": "Remote",
      "workModel": "Hybrid",
      "salaryMin": 120.0,
      "salaryMax": 144.0,
      "type": "Full-time",
      "description": "Looking for Python expert",
      "requirements": [
        "Python",
        "SQL"
      ],
      "match": {
        "jobId": "job-2",
        "score": 93,
        "reasons": {
          "skills": "Votre profil de Python correspond idéalement aux compétences demandées pour ce poste de Python Data Scientist.",
          "location": "Le statut hybride répond parfaitement à vos critères.",
          "salary": "Votre attente salariale est en phase avec la grille de l'entreprise.",
          "jobType": "Le poste cadre avec vos projets professionnels."
        }
      },
      "applied": false,
      "applicationStatus": null
    }
  ]
}
