/**
 * Import function triggers from their respective submodules:
 *
 * import {onCall} from "firebase-functions/v2/https";
 * import {onDocumentWritten} from "firebase-functions/v2/firestore";
 *
 * See a full list of supported triggers at https://firebase.google.com/docs/functions
 */

import {setGlobalOptions} from "firebase-functions";
import {onRequest} from "firebase-functions/https";
import * as logger from "firebase-functions/logger";

// Start writing functions
// https://firebase.google.com/docs/functions/typescript

// For cost control, you can set the maximum number of containers that can be
// running at the same time. This helps mitigate the impact of unexpected
// traffic spikes by instead downgrading performance. This limit is a
// per-function limit. You can override the limit for each function using the
// `maxInstances` option in the function's options, e.g.
// `onRequest({ maxInstances: 5 }, (req, res) => { ... })`.
// NOTE: setGlobalOptions does not apply to functions using the v1 API. V1
// functions should each use functions.runWith({ maxInstances: 10 }) instead.
// In the v1 API, each function can only serve one request per container, so
// this will be the maximum concurrent request count.
setGlobalOptions({ maxInstances: 10 });


// Simple API endpoint
export const helloWorld = onRequest((request, response) => {
	logger.info("Hello logs!", {structuredData: true});
	response.send("Hello from Firebase!");
});

// Example: Database connection (Firestore)
import * as admin from "firebase-admin";
admin.initializeApp();

export const getData = onRequest(async (req, res) => {
		try {
			const snapshot = await admin.firestore().collection("sampleCollection").get();
			const data = snapshot.docs.map(doc => doc.data());
			res.json({ success: true, data });
		} catch (error) {
			const errMsg = (error instanceof Error) ? error.message : String(error);
			res.status(500).json({ success: false, error: errMsg });
		}
});

// Example: Authentication stub
export const checkAuth = onRequest((req, res) => {
	const authHeader = req.headers.authorization;
	if (!authHeader) {
		res.status(401).json({ success: false, message: "No auth token provided" });
		return;
	}
	// Here you would verify the token with Firebase Auth
	res.json({ success: true, message: "Auth token received (stub)" });
});
