import QRScanner from "/lib/qr-scanner/qr-scanner.min.js";
QRScanner.WORKER_PATH = "/lib/qr-scanner/qr-scanner-worker.min.js";
let videoElem = document.getElementById("scanner");
let qrScanner = new QRScanner(videoElem, (result) => postScan(result));
QRScanner.hasCamera().then((hasCamera) => {
  if (!hasCamera) {
    cleanUp();
  } else {
    qrScanner.start();
  }
});
function postScan(data) {
  console.log(data);
  document.getElementById("user_id").value = data;
  cleanUp();
}

function cleanUp() {
  videoElem.style.display = "none";
  qrScanner.stop();
  qrScanner.destroy();
  qrScanner = null;
}
