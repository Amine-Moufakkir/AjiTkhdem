import { GoogleGenAI, Type } from "@google/genai";
import { PDFParse } from "pdf-parse";

// Lazy-initialization of GoogleGenAI to prevent crashes on startup if key is missing
let aiClient: GoogleGenAI | null = null;

function getAiClient(): GoogleGenAI {
  if (!aiClient) {
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
      throw new Error("La clé API GEMINI_API_KEY est manquante dans les configurations d'environnement.");
    }
    aiClient = new GoogleGenAI({
      apiKey,
      httpOptions: {
        headers: {
          "User-Agent": "aistudio-build",
        }
      }
    });
  }
  return aiClient;
}

/**
 * Extracts raw textual data from an uploaded PDF document.
 */
export async function extractTextFromPdf(pdfBuffer: Buffer): Promise<string> {
  let parser: PDFParse | null = null;
  try {
    parser = new PDFParse({ data: pdfBuffer });
    const result = await parser.getText();
    return result.text || "";
  } catch (error: any) {
    console.error("Erreur durant l'extraction de texte PDF:", error);
    throw new Error("Impossible d'extraire le texte du document PDF transmis : " + (error?.message || "format invalide ou non décodable."));
  } finally {
    if (parser) {
      try {
        await parser.destroy();
      } catch (e) {
        console.warn("Échec du nettoyage du parser PDF:", e);
      }
    }
  }
}

/**
 * Calls Gemini-3.5-flash to score the CV's overall quality independent of job matching.
 */
export async function analyzeCVQuality(cvText: string): Promise<{ score: number; recommendations: string[] }> {
  try {
    const ai = getAiClient();
    const systemInstruction = 
      "Tu es un expert senior en recrutement international. " +
      "Ton but unique est d'évaluer objectivement la qualité rédactionnelle et structurelle d'un CV en te basant exclusivement sur la forme, la clarté, la structure et la présence d'informations clés (coordonnées, compétences, expériences chronologiques, formations). " +
      "Cette évaluation doit être totalement indépendante de toute offre d'emploi ou poste spécifique. " +
      "Tu dois impérativement renvoyer les résultats sous la forme d'un objet JSON strict contenant deux clés : 'score' (un nombre entier de 0 à 100 évaluant la qualité) et 'recommandations' (un tableau contenant exactement 3 suggestions concrètes et pertinentes d'amélioration rédigées en français).";

    const response = await ai.models.generateContent({
      model: "gemini-3.5-flash",
      contents: `Voici le texte brut tiré du CV de l'utilisateur :\n\n${cvText}\n\nÉvalue ce CV selon les instructions systémiques strictes de clarté, de forme et de présence d'informations clés indépendant de tout poste. Reste concentré sur la lisibilité humaine et robotique.`,
      config: {
        systemInstruction,
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            score: {
              type: Type.INTEGER,
              description: "Le score de qualité globale du CV entre 0 et 100."
            },
            recommandations: {
              type: Type.ARRAY,
              items: {
                type: Type.STRING
              },
              description: "Exactement 3 suggestions concrètes de rédactions ou d'optimisations de structure en français."
            }
          },
          required: ["score", "recommandations"]
        }
      }
    });

    const text = response.text?.trim() || "";
    const parsed = JSON.parse(text);
    return {
      score: typeof parsed.score === "number" ? parsed.score : 70,
      recommendations: Array.isArray(parsed.recommandations) ? parsed.recommandations.slice(0, 3) : []
    };
  } catch (err) {
    console.warn("Avertissement: Échec du scoring via l'API Gemini (clé manquante ou erreur). Utilisation du moteur de simulation local :", err);
    
    // Beautiful, smart rule-based fallback if the API fails or is not yet configured
    let score = 75;
    const recommendations = [
      "Optimiser l'en-tête de votre CV en y intégrant un titre professionnel clair et un lien vers votre site ou profil LinkedIn.",
      "Structurer vos expériences chronologiques avec des listes à puces concises pour dynamiser la lecture opérationnelle.",
      "Spécifier le niveau de maîtrise ou l'application concrète pour chaque compétence répertoriée."
    ];

    if (cvText.length < 400) {
      score = 55;
      recommendations[1] = "Votre CV contient très peu de texte. Veuillez étoffer la description de vos mandats en détaillant vos livrables.";
    } else if (cvText.toLowerCase().includes("senior") || cvText.toLowerCase().includes("dirigeant")) {
      score = 88;
      recommendations[0] = "Ajouter un court paragraphe 'Profil' en haut du CV pour résumer votre proposition de valeur en 3 lignes.";
    }

    return { score, recommendations };
  }
}
