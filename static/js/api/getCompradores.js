export async function getCompradores() {
    const response = await fetch("/get/compradores")
    const data = await response.json()
    return data
}