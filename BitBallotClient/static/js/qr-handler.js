var qrScanner;
var videoElem;
$(document).ready(function () {
  $("#open-qr").click(function () {
    if(qrScanner) {
      cleanUp();
    } else{
      setUp();
    }
  });
});
import QRScanner from "/lib/qr-scanner/qr-scanner.min.js";


// QRScanner.hasCamera().then((hasCamera) => {
//   if (hasCamera) {
//     setUp();
//   }
// });

function setUp() {
  QRScanner.WORKER_PATH = "/lib/qr-scanner/qr-scanner-worker.min.js";
  videoElem = document.getElementById("scanner");
  videoElem.style.display = "inline";
  qrScanner = new QRScanner(videoElem, (result) => postScan(result));
  qrScanner.start();
}

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
