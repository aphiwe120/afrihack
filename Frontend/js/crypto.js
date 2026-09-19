function hexToBytes(hex) {
  if (!/^[\da-f]{64}$/i.test(hex)) throw new Error('The encryption key must contain 32 bytes encoded as hexadecimal.');
  return Uint8Array.from(hex.match(/.{2}/g), value => parseInt(value, 16));
}

function bytesToHex(bytes) {
  return [...bytes].map(value => value.toString(16).padStart(2, '0')).join('');
}

export async function encryptFile(file, masterKeyHex) {
  const key = await crypto.subtle.importKey('raw', hexToBytes(masterKeyHex), 'AES-GCM', false, ['encrypt']);
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const encrypted = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, await file.arrayBuffer());
  return { blob: new Blob([encrypted], { type: 'application/octet-stream' }), ivHex: bytesToHex(iv) };
}

export async function decryptBlob(blob, masterKeyHex, ivHex, type = 'application/octet-stream') {
  const key = await crypto.subtle.importKey('raw', hexToBytes(masterKeyHex), 'AES-GCM', false, ['decrypt']);
  const plain = await crypto.subtle.decrypt({ name: 'AES-GCM', iv: hexToBytes(ivHex) }, key, await blob.arrayBuffer());
  return new Blob([plain], { type });
}
