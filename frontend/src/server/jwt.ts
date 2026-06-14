import crypto from 'crypto';

const JWT_SECRET = process.env.JWT_SECRET || 'auto-apply-ai-super-secret-key-2026-06-06';

// Helper to base64url encode buffers/strings
function base64urlEncode(str: string | Buffer): string {
  const buf = typeof str === 'string' ? Buffer.from(str) : str;
  return buf.toString('base64')
    .replace(/=/g, '')
    .replace(/\+/g, '-')
    .replace(/\//g, '_');
}

// Helper to base64url decode strings
function base64urlDecode(str: string): string {
  let base64 = str.replace(/-/g, '+').replace(/_/g, '/');
  while (base64.length % 4) {
    base64 += '=';
  }
  return Buffer.from(base64, 'base64').toString('utf8');
}

export class JWT {
  static sign(payload: object, expiresInMinutes = 600): string {
    const header = { alg: 'HS256', typ: 'JWT' };
    const exp = Math.floor(Date.now() / 1000) + expiresInMinutes * 60;
    const fullPayload = { ...payload, exp };

    const encodedHeader = base64urlEncode(JSON.stringify(header));
    const encodedPayload = base64urlEncode(JSON.stringify(fullPayload));

    const signatureInput = `${encodedHeader}.${encodedPayload}`;
    const hmac = crypto.createHmac('sha256', JWT_SECRET);
    hmac.update(signatureInput);
    const signature = base64urlEncode(hmac.digest());

    return `${signatureInput}.${signature}`;
  }

  static verify(token: string): any | null {
    if (!token) return null;
    const parts = token.split('.');
    if (parts.length !== 3) return null;

    const [encodedHeader, encodedPayload, signature] = parts;
    const signatureInput = `${encodedHeader}.${encodedPayload}`;

    const hmac = crypto.createHmac('sha256', JWT_SECRET);
    hmac.update(signatureInput);
    const expectedSignature = base64urlEncode(hmac.digest());

    if (signature !== expectedSignature) {
      return null; // Signature verification failed
    }

    try {
      const payload = JSON.parse(base64urlDecode(encodedPayload));
      // Check timestamp expiration
      if (payload.exp && Math.floor(Date.now() / 1000) > payload.exp) {
        return null; // Expired token
      }
      return payload;
    } catch {
      return null;
    }
  }
}
