from Poseidon_BSC_Simplify import Utils

if __name__ == "__main__":
    PrivateKey = input("PrivateKey:")
    print(f"PrivateKeyBase64:{Utils.SimplyEncryptPrivateKey(PrivateKey=PrivateKey)}")
