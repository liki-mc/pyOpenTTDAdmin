#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "monocypher.h" // declares crypto_aead_ctx, crypto_aead_init_x, crypto_aead_read/write, crypto_aead_lock/unlock, crypto_wipe

namespace py = pybind11;

PYBIND11_MODULE(pymonocypher, m) {
    // Expose the C struct type under Python name CryptoAeadCtx
    py::class_<crypto_aead_ctx>(m, "CryptoAeadCtx", "Crypto AEAD context, matches the exact crypto OpenTTD uses.")
    
        
		.def(py::init([](py::bytes key, py::bytes nonce24) {
			std::string k = key; std::string n = nonce24;
			if (k.size() != 32) throw std::runtime_error("key must be 32 bytes");
			if (n.size() != 24) throw std::runtime_error("nonce must be 24 bytes");
			crypto_aead_ctx ctx;
			crypto_aead_init_x(&ctx,
			reinterpret_cast<const uint8_t*>(k.data()),
			reinterpret_cast<const uint8_t*>(n.data()));
			return ctx;
		}), py::arg("key"), py::arg("nonce24"),
		"Construct and init from key and nonce.")

        .def("read", [](crypto_aead_ctx &self, py::bytes data, py::bytes aad_b = py::bytes())
            {
            std::string s = data;
            if (s.size() < 16) throw std::runtime_error("combined too short for mac");
            std::string mac(s.data(), 16);
            std::string cipher(s.data() + 16, s.size() - 16);
            std::string a = aad_b;
            
            std::vector<uint8_t> out(cipher.size());
            int rc = crypto_aead_read(&self, out.data(),
                                      reinterpret_cast<const uint8_t*>(mac.data()),
                                      a.empty()?nullptr:reinterpret_cast<const uint8_t*>(a.data()), a.size(),
                                      reinterpret_cast<const uint8_t*>(cipher.data()), cipher.size());
            if (rc != 0) throw std::runtime_error("authentication failed");
            return py::bytes(reinterpret_cast<char*>(out.data()), out.size());
            }, 
            py::arg("data"), 
            py::arg("aad") = py::bytes(),
            "Verify and decrypt ciphertext with the context. Raises on auth failure; returns plaintext."
        )

        .def("write", [](crypto_aead_ctx &self, py::bytes plain_b, py::bytes aad_b = py::bytes())
            {
		        std::string p = plain_b, a = aad_b;
		        std::vector<uint8_t> ct(p.size());
		        uint8_t mac[16];
		        crypto_aead_write(&self, ct.data(), mac,
		                                   a.empty()?nullptr:reinterpret_cast<const uint8_t*>(a.data()), a.size(),
		                                   reinterpret_cast<const uint8_t*>(p.data()), p.size());
		        
		        
		        
		        std::string data(reinterpret_cast<const char*>(mac), 16);
                data.append(reinterpret_cast<const char*>(ct.data()), ct.size());
                return py::bytes(data);
		    },
		    py::arg("plaintext"), 
		    py::arg("aad") = py::bytes(),
		    "Encrypt plaintext with the context. Returns (mac, ciphertext)."
        )
        
        .def("wipe", [](crypto_aead_ctx &self){ crypto_wipe(&self, sizeof(self)); }, "Securely wipe the context (zeroes key/material).")
        
        .def_static("lock", [](py::bytes plain_b, py::bytes key, py::bytes nonce24, py::bytes aad_b = py::bytes())
            {
		        std::string p = plain_b, k = key, n = nonce24, a = aad_b;
		        if (k.size() != 32) throw std::runtime_error("key must be 32 bytes");
		        if (n.size() != 24) throw std::runtime_error("nonce must be 24 bytes");
		        std::vector<uint8_t> ct(p.size());
		        uint8_t mac[16];
		        crypto_aead_lock(ct.data(), mac,
		                         reinterpret_cast<const uint8_t*>(k.data()),
		                         reinterpret_cast<const uint8_t*>(n.data()),
		                         a.empty()?nullptr:reinterpret_cast<const uint8_t*>(a.data()), a.size(),
		                         reinterpret_cast<const uint8_t*>(p.data()), p.size());
		        return py::make_tuple(py::bytes(reinterpret_cast<char*>(mac), 16),
		                              py::bytes(reinterpret_cast<char*>(ct.data()), ct.size()));
		    },
		    py::arg("plaintext"), 
		    py::arg("key"), 
		    py::arg("nonce24"), 
		    py::arg("aad") = py::bytes(),
		    "Stateless encrypt: returns (mac, ciphertext)."
        )
        
		.def_static("unlock", [](py::bytes mac_b, py::bytes cipher_b, py::bytes key, py::bytes nonce24, py::bytes aad_b = py::bytes())
		    {
			    std::string macs = mac_b, c = cipher_b, k = key, n = nonce24, a = aad_b;
			    if (macs.size() != 16) throw std::runtime_error("mac must be 16 bytes");
			    if (k.size() != 32) throw std::runtime_error("key must be 32 bytes");
			    if (n.size() != 24) throw std::runtime_error("nonce must be 24 bytes");
			    std::vector<uint8_t> out(c.size());
			    int rc = crypto_aead_unlock(out.data(),
			                                reinterpret_cast<const uint8_t*>(macs.data()),
			                                reinterpret_cast<const uint8_t*>(k.data()),
			                                reinterpret_cast<const uint8_t*>(n.data()),
			                                a.empty()?nullptr:reinterpret_cast<const uint8_t*>(a.data()), a.size(),
			                                reinterpret_cast<const uint8_t*>(c.data()), c.size());
			    if (rc != 0) throw std::runtime_error("authentication failed");
			    return py::bytes(reinterpret_cast<char*>(out.data()), out.size());
			},
			py::arg("mac"), 
			py::arg("ciphertext"), 
			py::arg("key"), 
			py::arg("nonce24"), 
			py::arg("aad") = py::bytes(),
			"Stateless decrypt: returns plaintext or raises on auth failure."
		)
        ;
    
	m.def("x25519",
	    [](py::bytes our_secret, py::bytes their_public) {
	        std::string a = our_secret, b = their_public;
	        if (a.size() != 32) throw std::runtime_error("our_secret must be 32 bytes");
	        if (b.size() != 32) throw std::runtime_error("their_public must be 32 bytes");
	        uint8_t shared[32];
	        crypto_x25519(shared,
	                      reinterpret_cast<const uint8_t*>(a.data()),
	                      reinterpret_cast<const uint8_t*>(b.data()));
	        return py::bytes(reinterpret_cast<char*>(shared), 32);
	    },
	    py::arg("our_secret"), py::arg("their_public"),
	    "Compute X25519 shared secret from our_secret(32) and their_public(32). Returns 32-byte shared secret."
	);

	// blake2b: staticmethod -> compute hash over a sequence of byte chunks
	m.def("blake2b",
	    [](size_t hash_size, py::iterable chunks) {
	        if (hash_size == 0 || hash_size > 64) throw std::runtime_error("hash_size must be 1..64");
	        crypto_blake2b_ctx ctx;
	        crypto_blake2b_init(&ctx, hash_size);
	        for (auto item : chunks) {
				// accept any bytes-like via the buffer protocol
				py::buffer buf = py::cast<py::buffer>(item);
				py::buffer_info info = buf.request();
				if (info.ptr == nullptr) throw std::runtime_error("invalid buffer item");
				const uint8_t* data = static_cast<const uint8_t*>(info.ptr);
				size_t len = static_cast<size_t>(info.size) * static_cast<size_t>(info.itemsize);
				crypto_blake2b_update(&ctx, data, len);
			}
	        std::vector<uint8_t> out(hash_size);
	        crypto_blake2b_final(&ctx, out.data());
	        return py::bytes(reinterpret_cast<char*>(out.data()), out.size());
	    },
	    py::arg("hash_size"), py::arg("chunks"),
	    "Compute BLAKE2b hash of concatenated chunks. 'chunks' is an iterable of bytes-like objects. Returns digest bytes."
	);

	// shared_keys: classmethod alias to x25519 (keeps semantic naming)
	m.def("shared_keys",
	    [](py::bytes our_secret, py::bytes their_public) {
	        // reuse the same implementation as x25519
	        std::string a = our_secret, b = their_public;
	        if (a.size() != 32) throw std::runtime_error("our_secret must be 32 bytes");
	        if (b.size() != 32) throw std::runtime_error("their_public must be 32 bytes");
	        uint8_t shared[32];
	        crypto_x25519(shared,
	                      reinterpret_cast<const uint8_t*>(a.data()),
	                      reinterpret_cast<const uint8_t*>(b.data()));
	        return py::bytes(reinterpret_cast<char*>(shared), 32);
	    },
	    py::arg("our_secret"), py::arg("their_public"),
	    "Alias for x25519; returns 32-byte shared secret."
	);
	
	m.def("get_public_key", 
	    [](py::bytes secret_key) {
	        std::string skey = secret_key;
	        if (skey.size() != 32) throw std::runtime_error("secret_key must be 32 bytes");
	        uint8_t pkey[32];
	        crypto_x25519_public_key(pkey, reinterpret_cast<const uint8_t*>(skey.data()));
	        return py::bytes(reinterpret_cast<char*>(pkey), 32);
	    },
	    py::arg("secret_key"),
	    "Get public key for x25519 from private key."
	);
}









