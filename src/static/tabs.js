function piechartOrTable(evt, type) {
  var i, holdingsTabContent, holdingsTabLinks;
  holdingsTabContent = document.getElementsByClassName("holdingsTabContent");
  for (i = 0; i < holdingsTabContent.length; i++) {
    holdingsTabContent[i].style.display = "none";
  }
  holdingsTabLinks = document.getElementsByClassName("holdingsTabLinks");
  for (i = 0; i < holdingsTabLinks.length; i++) {
    holdingsTabLinks[i].className = holdingsTabLinks[i].className.replace(" active", "");
  }
  document.getElementById(type).style.display = "block";
  evt.currentTarget.className += " active";
}


function selectPeriod(evt, period) {
  var i, historyTabContent, historyTabLinks;
  historyTabContent = document.getElementsByClassName("historyTabContent");
  for (i = 0; i < historyTabContent.length; i++) {
    historyTabContent[i].style.display = "none";
  }
  historyTabLinks = document.getElementsByClassName("historyTabLinks");
  for (i = 0; i < historyTabLinks.length; i++) {
    historyTabLinks[i].className = historyTabLinks[i].className.replace(" active", "");
  }
  document.getElementById(period).style.display = "block";
  evt.currentTarget.className += " active";
}

