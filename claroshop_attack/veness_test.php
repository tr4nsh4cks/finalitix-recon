<?php
/* Veness AES-CTR validation harness — ClaroShop datostarjeta key */
require_once __DIR__ . '/AesCtr.php';

$KEY = '8L84j3x3yZY894gyEwFNhDSPSrfyHf9WA'; // 32 chars -> 256 bits

echo "=== PHP " . phpversion() . " ===\n";
echo "Key length: " . strlen($KEY) . " chars\n\n";

// --- 1. Derive the internal key exactly like AesCtr does, print hex for cross-impl check ---
function derive_key_hex($password, $nBits) {
    $nBytes = $nBits / 8;
    $pwBytes = array();
    for ($i = 0; $i < $nBytes; $i++) $pwBytes[$i] = ord(substr($password, $i, 1)) & 0xff;
    $key = Aes::cipher($pwBytes, Aes::keyExpansion($pwBytes));
    $key = array_merge($key, array_slice($key, 0, $nBytes - 16));
    return implode('', array_map(function($b){ return sprintf('%02x', $b); }, $key));
}

echo "[KEY-DERIVATION CHECK]\n";
echo "derived_key_256_hex=" . derive_key_hex($KEY, 256) . "\n";
echo "derived_key_128_hex=" . derive_key_hex($KEY, 128) . "\n\n";

// --- 2. Roundtrip tests at 256 bits ---
echo "[ROUNDTRIP 256-bit]\n";
$samples = array(
    '4111111111111111',
    '5499 3800 0000 0004',
    '123',
    '4916 1234 5678 9012|123|12/28',
    utf8_encode('José Pérez Ñandú'),
);
$ok = 0; $fail = 0;
foreach ($samples as $s) {
    $enc = AesCtr::encrypt($s, $KEY, 256);
    $dec = AesCtr::decrypt($enc, $KEY, 256);
    $match = ($dec === $s) ? 'OK' : 'FAIL';
    if ($match === 'OK') $ok++; else $fail++;
    echo "  [$match] plain='$s' enc=$enc dec='$dec'\n";
}
echo "roundtrip: $ok OK / $fail FAIL\n\n";

// --- 3. Fixed-nonce deterministic vector (for Python cross-check) ---
// Replicate encrypt with a FIXED counter block so output is reproducible across languages.
echo "[FIXED-NONCE VECTOR 256-bit] (for Python/Java cross-validation)\n";
function veness_encrypt_fixed($plaintext, $password, $nBits, $nonceMs, $nonceRnd, $nonceSec) {
    $blockSize = 16;
    $nBytes = $nBits / 8;
    $pwBytes = array();
    for ($i = 0; $i < $nBytes; $i++) $pwBytes[$i] = ord(substr($password, $i, 1)) & 0xff;
    $key = Aes::cipher($pwBytes, Aes::keyExpansion($pwBytes));
    $key = array_merge($key, array_slice($key, 0, $nBytes - 16));

    $counterBlock = array();
    for ($i = 0; $i < 2; $i++) $counterBlock[$i] = ($nonceMs >> ($i * 8)) & 0xff;
    for ($i = 0; $i < 2; $i++) $counterBlock[$i + 2] = ($nonceRnd >> ($i * 8)) & 0xff;
    for ($i = 0; $i < 4; $i++) $counterBlock[$i + 4] = ($nonceSec >> ($i * 8)) & 0xff;

    $ctrTxt = '';
    for ($i = 0; $i < 8; $i++) $ctrTxt .= chr($counterBlock[$i]);

    $keySchedule = Aes::keyExpansion($key);
    $blockCount = ceil(strlen($plaintext) / $blockSize);
    $ciphertxt = array();
    for ($b = 0; $b < $blockCount; $b++) {
        for ($c = 0; $c < 4; $c++) $counterBlock[15 - $c] = ($b >> ($c * 8)) & 0xff;
        for ($c = 0; $c < 4; $c++) $counterBlock[15 - $c - 4] = 0;
        $cipherCntr = Aes::cipher($counterBlock, $keySchedule);
        $blockLength = $b < $blockCount - 1 ? $blockSize : (strlen($plaintext) - 1) % $blockSize + 1;
        $cipherByte = array();
        for ($i = 0; $i < $blockLength; $i++) {
            $cipherByte[$i] = chr($cipherCntr[$i] ^ ord(substr($plaintext, $b * $blockSize + $i, 1)));
        }
        $ciphertxt[$b] = implode('', $cipherByte);
    }
    return base64_encode($ctrTxt . implode('', $ciphertxt));
}

// nonce: ms=1, rnd=2, sec=3  -> counter block bytes: 01 00 02 00 03 00 00 00
$vec_plain = '4111111111111111';
$vec_enc = veness_encrypt_fixed($vec_plain, $KEY, 256, 1, 2, 3);
echo "  plain=$vec_plain\n";
echo "  nonce_bytes_hex=0100020003000000\n";
echo "  ciphertext_b64=$vec_enc\n";
$vec_dec = AesCtr::decrypt($vec_enc, $KEY, 256);
echo "  decrypt_via_AesCtr=" . $vec_dec . " (" . ($vec_dec === $vec_plain ? 'OK' : 'FAIL') . ")\n\n";

// --- 4. If ciphertext samples are passed as CLI args, decrypt them ---
if (isset($argv[1])) {
    echo "[DECRYPTING PROVIDED SAMPLES @ 256/192/128 bits]\n";
    for ($a = 1; $a < $argc; $a++) {
        $ct = $argv[$a];
        echo "  sample: $ct\n";
        foreach (array(256, 192, 128) as $bits) {
            $d = @AesCtr::decrypt($ct, $KEY, $bits);
            $printable = preg_match('/^[\x20-\x7e]+$/', $d) ? 'PRINTABLE' : 'binary';
            echo "    ${bits}-bit -> '$d' [$printable]\n";
        }
    }
}
echo "\nDONE\n";
