var gDemoDataFilesByDirectory = {};


//=============================================================================
// initialize() - code entry for the demo application
// (it is called from demo.html)
//=============================================================================
function initialize() {
  document.title = "DIAG Web Application";
  // create the instance
  var diagApp = new DiagApplication();
  diagApp.init();
  // register the callback that is called when all module contexts are created
  gApp.setModuleContextsReadyCallback(diagApp.moduleContextsReady);
}


//=============================================================================
// The DiagApplication class
//=============================================================================
function DiagApplication() {
  var self = this;
  
  
  //=============================================================================
  // init() - prepares the divs for the module panels and the demo data browser
  //=============================================================================
  this.init = function() {
    gApp.showLoadDialog();

    // create layouting elements    
    var panelDiv = document.createElement("div");
    panelDiv.setAttribute("class", "panelDiv");
    panelDiv.setAttribute("style", "width: 100%");
    gApp.body.appendChild(panelDiv);
    
    // create and add the DemoWebApplication module panel
    // - the first parameter must be the exact name of the macro module that will
    //   be instantiated on the server
    // - the second parameter can be any id that is unique in the html document
    var isLoginRequired = true;
    var moduleContextDiv = gApp.createModuleContextDiv("COMICWebWorkstation", "WebViewportModulePanelDiv", isLoginRequired);
    moduleContextDiv.setAttribute("style", "width: 100%");
    panelDiv.appendChild(moduleContextDiv);

    var viewersDiv = document.createElement("div");
    viewersDiv.id = "Window_Viewers";
    
    function createLogo() {
      var url = window.location.protocol + "//" + window.location.host + "/Packages/Visia/EnterpriseApp/Resources/Images/Branding/BackgroundLogo.png";
      var img = document.createElement("img");
      img.src = url;
      var tr = viewersTable.insertRow(2);
      tr.setAttribute("class", "logo");
      var c = tr.insertCell(0);
      c.appendChild(img);
    }
    //createLogo();
    
    // create a div for diagnosis messages
    function createDiagnosisPanel() {
      var t = document.createElement("table");
      t.setAttribute("class", "diagnosisTable");
      var c = bodyTable.insertRow(1).insertCell(0);
      c.setAttribute("colspan", "2");
      c.appendChild(t);
      
      var div = document.createElement("div");
      div.setAttribute("class", "diagnosisDiv");    
      var contentDiv = document.createElement("div"); 
      contentDiv.setAttribute("class", "diagnosisContentDiv");
      contentDiv.id = "DiagnosisPanel";
      div.appendChild(contentDiv);
      t.insertRow(0).insertCell(0).appendChild(div);
      
      var titleDiv = document.createElement("div");
      titleDiv.setAttribute("class", "captionDiv");
      titleDiv.innerHTML = "Diagnosis Console";
      t.insertRow(0).insertCell(0).appendChild(titleDiv);
    }
    
    if (gApp.showDiagnosisPanel()) {
      createDiagnosisPanel();
    }
  };

  
  //=============================================================================
  // moduleContextsReady() - this is registered as callback in the application
  // after all module contexts haven been created
  //=============================================================================
  this.moduleContextsReady = function () {
    if ("rotorOn" in gApp.getArguments()) {
      gApp.getModuleContext("WebViewportModulePanelDiv").getModule().setFieldValue("rotorOn", "true");
    }
    // hide the load dialog
    gApp.hideLoadDialog();
  };
}
