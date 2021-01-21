import QRScanner from '/lib/qr-scanner/qr-scanner.min.js';
QRScanner.WORKER_PATH = '/lib/qr-scanner/qr-scanner-worker.min.js';
let videoElem = document.getElementById("scanner");
const qrScanner = new QRScanner(videoElem, result => postScan(result));
qrScanner.start();
function postScan(data) {
    console.log(data);
    document.getElementById("user_id").value = data;
    qrScanner.stop();
}