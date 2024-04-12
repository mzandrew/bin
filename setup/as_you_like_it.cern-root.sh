#!/bin/bash -e

# written 2019-06-27 by mza
# last updated 2023-05-25 by mza
# the build dir is about 3GB after the build

# when trying it on ubuntu 20.04:
# E: Package 'libpython-dev' has no installation candidate
# when trying it on ubuntu 22.04:
# E: Package 'python-dev' has no installation candidate

#declare filename="root_v6.22.00.source.tar.gz"
#declare dirname="root-6.22.00"

declare -i np=$(grep -c "^processor" /proc/cpuinfo)
declare -i j=$np
if [ -e /etc/rpi-issue ]; then
	j=1
	echo "dropping j to 1"
fi

declare -i MiB=1024

function add_swap_if_necessary {
	if [ ! -e /swap ]; then
		echo "generating $MiB MiB /swap file..."
		sudo dd if=/dev/zero of=/swap bs=$((1024*1024)) count=$MiB
		sudo chmod 600 /swap
		sudo mkswap /swap
		# this happens after the "exit 0" line, so is useless:
		#sudo sed -ie '/swapon/{h;s/.*/swapon \/swap/};${x;/^$/{s/.*/swapon \/swap/;H};x}' /etc/rc.local
		#echo "fix /etc/rc.local to do \"swapon /swap\" before the exit 0!"
	fi
	sudo swapon /swap || /bin/true
}

# https://root.cern.ch/build-prerequisites

function install_prerequisites_apt {
	#sudo nice apt -y install git dpkg-dev make g++ gcc binutils libx11-dev libxpm-dev libxft-dev libxext-dev gfortran libfftw3-dev libjpeg-dev libgif-dev libtiff-dev libcfitsio-dev libxml2-dev uuid-dev davix-dev libgfal2-dev libgl2ps-dev libpcre2-dev liblz4-dev libgsl-dev libssl-dev libgfal2-dev libtbb-dev gsl-bin libpython-dev
	#sudo nice apt -y install "cmake>=3.6"
	sudo nice apt -y install git dpkg-dev make g++ gcc binutils libx11-dev libxpm-dev libxft-dev libxext-dev python3-dev gfortran cmake libfftw3-dev libjpeg-dev libgif-dev libtiff-dev libcfitsio-dev libxml2-dev uuid-dev davix-dev libgfal2-dev libgl2ps-dev libpcre2-dev liblz4-dev libgsl-dev libssl-dev libgfal2-dev libtbb-dev gsl-bin libpython2.7-dev
	# libcblas-dev libcblas3
	# Enabled support for:  asimage astiff builtin_afterimage builtin_clang builtin_ftgl builtin_glew builtin_llvm builtin_tbb builtin_vdt builtin_xxhash clad cling cxx11 davix exceptions explicitlink fftw3 fitsio gdml http imt mathmore opengl pch pythia8 python roofit shared ssl thread tmva tmva-cpu tmva-pymva vdt x11 xft xml
}

function install_prerequisites_yum {
	sudo nice yum -y update
	sudo nice yum -y upgrade
	sudo nice yum -y install git cmake gcc-c++ gcc binutils libX11-devel libXpm-devel libXft-devel libXext-devel gcc-gfortran openssl-devel pcre-devel mesa-libGL-devel mesa-libGLU-devel glew-devel ftgl-devel mysql-devel fftw-devel cfitsio-devel graphviz-devel avahi-compat-libdns_sd-devel python-devel libxml2-devel
	# libldap-dev gsl-static
}

function install_prerequisites_pac {
	sudo pacman --needed --noconfirm -Syu
#	sudo pacman --needed --noconfirm -S
}

declare -i redhat=0 SL6=0 SL7=0 deb=0
if [ -e /etc/redhat-release ]; then
	redhat=1
	set +e
	SL6=$(grep -c "Scientific Linux release 6" /etc/redhat-release)
	SL7=$(grep -c "Scientific Linux release 7" /etc/redhat-release)
	set -e
elif [ -e /etc/debian_version ]; then
	deb=1
elif [ -e /etc/arch-release ]; then
	arch=1
else
	echo "what kind of linux is this?"
	exit 1
fi
if [ $deb -gt 0 ]; then
	install_prerequisites_apt
elif [ $redhat -gt 0 ]; then
	install_prerequisites_yum
elif [ $arch -gt 0 ]; then
	install_prerequisites_pac
fi

#add_swap_if_necessary
declare build="${HOME}/build"
cd
mkdir -p $build
cd $build

function build_and_install_cmake_from_source {
	sudo apt -y remove cmake cmake-data
	if [ ! -d "cmake" ]; then
		if [ ! -e "cmake-3.15.5.tar.gz" ]; then
			wget https://github.com/Kitware/CMake/releases/download/v3.15.5/cmake-3.15.5.tar.gz
		fi
		tar -xzf "cmake-3.15.5.tar.gz"
	fi
	cd "cmake-3.15.5"
	nice ./configure
	nice gmake
	sudo make install
	sudo chmod o+rx /usr/local/share/cmake-3.15
}

# this mostly uninstalls any old versions of cern root:
if [ -e /usr/local/bin/thisroot.sh ]; then
	echo "existing install of CERN ROOT found.  removing..."
	cd /usr/local/bin
	sudo mkdir -p junk
	for each in root* thisroot* setxrd* proofserv* memprobe rmkdepend genreflex xpdtest hadd hist2workspace; do
		if [ -e "$each" ]; then
			sudo mv $each junk/
		fi
	done
	sudo rm -rf junk
	#ls -lart
#fi
#sudo touch /usr/local/lib/ROOT.py
#if [ -e /usr/local/lib/ROOT.py ]; then
	cd /usr/local/lib
	sudo mkdir -p junk
	for each in ROOT.py* libROOT* libPyROOT* libVMC* libPyMVA* _pythonization* cppyy.py* cmdLineUtils* libCore* libThread* libRint* libJupyROOT* libImt* *.pcm *.rootmap cppyy_backend cppyy ROOT JupyROOT JsMVA libXrd* libFTGL* libCore* libCling* libNew* libcppyy_backend* libJupyROOT* libRint.so libcomplexDict.so libmap2Dict.so libforward_listDict.so libvectorDict.so libdequeDict.so libvalarrayDict.so libmultimap2Dict.so libmultimapDict.so liblistDict.so libsetDict.so libmultisetDict.so libunordered* libmapDict.so libThread.so libcppyy* libImt.so libRIO.so libNet.so libXMLParser.so libMathCore.so libROOTVecOps.so libXMLIO.so libROOTTPython.so libSrvAuth.so libMultiProc.so libFFTW.so libRootAuth.so libSQLIO.so libNetx.so libRDAVIX.so libNetxNG.so libGX11.so libMatrix.so libRCsg.so libMathMore.so libGenVector.so libTree.so libSmatrix.so libPhysics.so libQuadp.so libROOTPythonizations* libProof.so libHist.so libFoam.so libGraf.so libSpectrum.so libUnfold.so libGeom.so libPostscript.so libGX11TTF.so libRHTTP.so libASImage.so libGdml.so libHtml.so libMinuit.so libFumili.so libGpad.so libGraf3d.so libGui.so libHistPainter.so libSpectrumPainter.so libRHTTPSniff.so libFITSIO.so libASImageGui.so libX3d.so libEG.so libGuiBld.so libGuiHtml.so libRecorder.so libSessionViewer.so libGeomPainter.so libRooFitCore.so libEGPythia8.so libTreePlayer.so libGed.so libMLP.so libSPlot.so libRooFit.so libFitPanel.so libROOTDataFrame.so libProofPlayer.so libTreeViewer.so libRooFitMore.so libGeomBuilder.so libRooStats.so libRGL.so libProofDraw.so libProofBench.so libHistFactory.so libGviz3d.so libTMVA.so libGenetic.so libEve.so libTMVAGui.so; do
		if [ -e "$each" ]; then
			sudo mv $each junk/
		fi
	done
	sudo rm -rf junk
	#ls -lart
	cd /usr/local/include
	sudo mkdir -p junk
	for each in TVirtualMCStack.h TVirtualMCSensitiveDetector.h TVirtualMC.h TVirtualMCGeometry.h TVirtualMCApplication.h TPySelector.h TPyROOTApplication.h TPyFitFunction.h TPyException.h TPyDispatcher.h TPainter3dAlgorithms.h TMCVerbose.h TMCtls.h TMCProcess.h TMCParticleType.h TMCOptical.h TMCAutoLock.h TLego.h TGeoMCGeometry.h TClingRuntime.h RooThreshEntry.h RooSharedPropertiesList.h RooMultiCatIter.h RooMapCatEntry.h RooCategorySharedProperties.h CommandLineOptionsHelp.h ZipZSTD.h ZipLZMA.h ZipLZ4.h X3DBuffer.h WidgetMessageTypes.h VectorizedTMath.h Varargs.h TZIPFile.h TXTRU.h TXNetSystem.h TXNetFileStager.h TXNetFile.h TXMLSetup.h TXMLPlayer.h TXMLParser.h TXMLNode.h TXMLFile.h TXMLEngine.h TXMLDocument.h TXMLAttr.h TX3DFrame.h TX11GL.h TWin32Thread.h TWin32ThreadFactory.h TWin32Mutex.h TWin32Condition.h TWin32AtomicCount.h TWebFile.h TWbox.h TVirtualX.h TVirtualViewer3D.h TVirtualTreePlayer.h TVirtualTableInterface.h TVirtualStreamerInfo.h TVirtualRWMutex.h TVirtualRefProxy.h TVirtualQConnection.h TVirtualPS.h TVirtualProofPlayer.h TVirtualPerfStats.h TVirtualPaveStats.h TVirtualPadPainter.h TVirtualPad.h TVirtualPadEditor.h TVirtualPacketizer.h TVirtualObject.h TVirtualMutex.h TVirtualMonitoring.h TVirtualMCDecayer.h TVirtualMagField.h TVirtualIsAProxy.h TVirtualIndex.h TVirtualHistPainter.h TVirtualGraphPainter.h TVirtualGL.h TVirtualGeoTrack.h TVirtualGeoPainter.h TVirtualGeoConverter.h TVirtualFitter.h TVirtualFFT.h TVirtualDragManager.h TVirtualCollectionProxy.h TVirtualCollectionIterators.h TVirtualAuth.h TVirtualArray.h TView.h TViewerX3D.h TViewer3DPad.h TView3D.h TVersionCheck.h TVectorT.h TVector.h TVectorfwd.h TVectorF.h TVectorFfwd.h TVectorD.h TVectorDfwd.h TVector3.h TVector2.h TUUID.h TUrl.h TUri.h TUnixSystem.h TUnfoldSys.h TUnfold.h TUnfoldDensity.h TUnfoldBinningXML.h TUnfoldBinning.h TUDPSocket.h TTVSession.h TTVLVContainer.h TTUBS.h TTUBE.h TTreeViewer.h TTreeTableInterface.h TTreeSQL.h TTreeRow.h TTreeResult.h TTreeReaderValue.h TTreeReaderUtils.h TTreeReader.h TTreeReaderGenerator.h TTreeReaderArray.h TTreeProxyGenerator.h TTreePlayer.h TTreePerfStats.h TTreeInput.h TTreeIndex.h TTree.h TTreeGeneratorBase.h TTreeFormulaManager.h TTreeFormula.h TTreeDrawArgsParser.h TTreeCloner.h TTreeCacheUnzip.h TTreeCache.h TTRD2.h TTRD1.h TTRAP.h TToggle.h TToggleGroup.h TTimeStamp.h TTimer.h TTime.h TThreadSlots.h TThreadPool.h TThreadImp.h TThread.h TThreadFactory.h TTF.h TText.h TTextEditor.h TTeXDump.h TTask.h TTabCom.h TSystem.h TSystemFile.h TSystemDirectory.h TSysEvtHandler.h TSynapse.h TSVG.h TSVDUnfold.h TStylePreview.h TStyleManager.h TStyle.h TStyleDialog.h TStructViewer.h TStructViewerGUI.h TStructNodeProperty.h TStructNode.h TStructNodeEditor.h TStringLong.h TString.h TStreamerInfo.h TStreamerInfoActions.h TStreamer.h TStreamerElement.h TStorage.h TStopwatch.h TStatus.h TStatusBitsChecker.h TStatsFeedback.h TStatistic.h TSSLSocket.h TSQLTableInfo.h TSQLStructure.h TSQLStatement.h TSQLServer.h TSQLRow.h TSQLResult.h TSQLObjectData.h TSQLMonitoring.h TSQLFile.h TSQLColumnInfo.h TSQLClassInfo.h TSPlot.h TSpline.h TSpider.h TSpiderEditor.h TSPHE.h TSpectrumTransform.h TSpectrum.h TSpectrumFit.h TSpectrum3.h TSpectrum2Transform.h TSpectrum2Painter.h TSpectrum2.h TSpectrum2Fit.h TSortedList.h TSocket.h TSlider.h TSliderBox.h TSlaveLite.h TSlave.h TSimpleAnalysis.h TShape.h TSessionViewer.h TSessionLogView.h TSessionDialogs.h TServerSocket.h TSeqCollection.h TSemaphore.h TSelVerifyDataSet.h TSelectorScalar.h TSelectorList.h TSelector.h TSelectorEntries.h TSelectorDraw.h TSecContext.h TSchemaRuleSet.h TSchemaRule.h TSchemaHelper.h TSAXParser.h TS3WebFile.h TS3HTTPRequest.h TRWLock.h TRotMatrix.h TRotation.h TRootSnifferStore.h TRootSniffer.h TRootSnifferFull.h TRootSecContext.h TRootIOCtor.h TRootHelpDialog.h TROOT.h TRootGuiFactory.h TRootGuiBuilder.h TRootEmbeddedCanvas.h TRootDialog.h TRootControlBar.h TRootContextMenu.h TRootCanvas.h TRootBrowserLite.h TRootBrowser.h TRootAuth.h TRootApplication.h TRolke.h TRobustEstimator.h TRint.h TRemoteObject.h TRegexp.h TRefTable.h TRefProxy.h TRef.h TRefCnt.h TRefArrayProxy.h TRefArray.h TreeUtils.h TRedirectOutputGuard.h TRecorder.h TRealData.h TRatioPlot.h TRandom.h TRandomGen.h TRandom3.h TRandom2.h TRandom1.h TQueryResultManager.h TQueryResult.h TQuaternion.h TQpVar.h TQpSolverBase.h TQpResidual.h TQpProbSparse.h TQpProbDens.h TQpProbBase.h TQpLinSolverSparse.h TQpLinSolverDens.h TQpLinSolverBase.h TQpDataSparse.h TQpDataDens.h TQpDataBase.h TQObject.h TQConnection.h TQCommand.h TQClass.h TPython.h TPythia8.h TPythia8Decayer.h TPyReturn.h TPyClassGenerator.h TPyArg.h TPSocket.h TPServerSocket.h TProtoClass.h TProofSuperMaster.h TProofServLite.h TProofServ.h TProofResourcesStatic.h TProofResources.h TProofQueryResult.h TProofProgressStatus.h TProofProgressMemoryPlot.h TProofProgressLog.h TProofProgressDialog.h TProofPlayerLite.h TProofPlayer.h TProofPerfAnalysis.h TProofOutputList.h TProofOutputFile.h TProofNodes.h TProofNodeInfo.h TProofMonSenderSQL.h TProofMonSenderML.h TProofMonSender.h TProofMgrLite.h TProofMgr.h TProofLog.h TProofLite.h TProofLimitsFinder.h TProof.h TProofDraw.h TProofDebug.h TProofCondor.h TProofChain.h TProofBenchTypes.h TProofBenchRun.h TProofBenchRunDataRead.h TProofBenchRunCPU.h TProofBench.h TProofBenchDataSet.h TProfile.h TProfile3D.h TProfile2Poly.h TProfile2D.h TProcPool.h TProcessUUID.h TProcessID.h TPrincipal.h TPrimary.h TPRegexp.h TPostScript.h TPosixThread.h TPosixThreadFactory.h TPosixMutex.h TPosixCondition.h TPolyMarker.h TPolyMarker3D.h TPolyLine.h TPolyLine3D.h TPoints.h TPointSet3D.h TPointSet3DGL.h TPoints3DABC.h TPoint.h TPluginManager.h TPieSlice.h TPieSliceEditor.h TPie.h TPieEditor.h TPGON.h TPerfStats.h TPDGCode.h TPDF.h TPCON.h TPaveText.h TPavesText.h TPaveStats.h TPaveStatsEditor.h TPaveLabel.h TPave.h TPaveClass.h TParticlePDG.h TParticle.h TParticleClassPDG.h TParameter.h TParallelMergingFile.h TParallelCoordVar.h TParallelCoordRange.h TParallelCoord.h TParallelCoordEditor.h TPARA.h TPaletteAxis.h TPadPainter.h TPad.h TPadEditor.h TPackMgr.h TPacketizerUnit.h TPacketizerMulti.h TPacketizer.h TPacketizerFile.h TPacketizerAdaptive.h TOutputListSelectorDataMap.h TOrdCollection.h TObjString.h TObjectTable.h TObjectSpy.h TObject.h TObjArray.h TNtuple.h TNtupleD.h TNotifyLink.h TNode.h TNodeDiv.h TNeuron.h TNetXNGSystem.h TNetXNGFileStager.h TNetXNGFile.h TNetFileStager.h TNetFile.h TNDArray.h TNamed.h TMutexImp.h TMutex.h TMultiLayerPerceptron.h TMultiGraph.h TMultiDimFit.h TMPWorkerTree.h TMPWorker.h TMPWorkerExecutor.h TMPClient.h TMonitor.h TMLPAnalyzer.h TMixture.h TMinuitMinimizer.h TMinuit.h TMethod.h TMethodCall.h TMethodArg.h TMessageHandler.h TMessage.h TMemStatShow.h TMemFile.h TMemberStreamer.h TMemberInspector.h TMehrotraSolver.h TMD5.h TMatrixTUtils.h TMatrixTSym.h TMatrixTSymCramerInv.h TMatrixTSparse.h TMatrixTLazy.h TMatrixT.h TMatrixTCramerInv.h TMatrixTBase.h TMatrix.h TMatrixFUtils.h TMatrixFUtilsfwd.h TMatrixFSym.h TMatrixFSymfwd.h TMatrixFSparse.h TMatrixFSparsefwd.h TMatrixFLazy.h TMatrixF.h TMatrixFfwd.h TMatrixFBase.h TMatrixFBasefwd.h TMatrixDUtils.h TMatrixDUtilsfwd.h TMatrixDSym.h TMatrixDSymfwd.h TMatrixDSymEigen.h TMatrixDSparse.h TMatrixDSparsefwd.h TMatrixDLazy.h TMatrixD.h TMatrixDfwd.h TMatrixDEigen.h TMatrixDBase.h TMatrixDBasefwd.h TMathText.h TMath.h TMathBase.h TMaterial.h TMarker.h TMarker3DBox.h TMap.h TMapFile.h TMakeProject.h TMacro.h TLorentzVector.h TLorentzRotation.h TLockPath.h TLockFile.h TListOfFunctionTemplates.h TListOfFunctions.h TListOfEnumsWithLock.h TListOfEnums.h TListOfDataMembers.h TList.h TLink.h TLine.h TLineEditor.h TLinearMinimizer.h TLinearFitter.h TLimit.h TLimitDataSource.h TLegend.h TLegendEntry.h TLeafS.h TLeafO.h TLeafObject.h TLeafL.h TLeafI.h TLeaf.h TLeafF.h TLeafF16.h TLeafElement.h TLeafD.h TLeafD32.h TLeafC.h TLeafB.h TLatex.h TKeyXML.h TKeySQL.h TKeyMapFile.h TKey.h TKDTree.h TKDTreeBinning.h TKDE.h TKDEFGT.h TKDEAdapter.h TIterator.h TIsAProxy.h TInterpreterValue.h TInterpreter.h TInspectorImp.h TInspectCanvas.h TInetAddress.h TIndArray.h TImagePlugin.h TImage.h TImageDump.h THYPE.h THttpWSHandler.h THttpServer.h THttpEngine.h THttpCallArg.h THtml.h THStack.h ThreadLocalStorage.h THostAuth.h THnSparse_Internal.h THnSparse.h THn.h THnChain.h THnBase.h THLimitsFinder.h THistPainter.h THelix.h THashTable.h THashList.h TH3S.h TH3I.h TH3.h TH3GL.h TH3F.h TH3D.h TH3C.h TH2S.h TH2Poly.h TH2I.h TH2.h TH2GL.h TH2F.h TH2Editor.h TH2D.h TH2C.h TH1S.h TH1K.h TH1I.h TH1.h TH1F.h TH1Editor.h TH1D.h TH1C.h TGXYLayout.h TGX11TTF.h TGX11.h TGWindow.h TGWidget.h TGView.h TGuiFactory.h TGuiBuilder.h TGuiBldNameFrame.h TGuiBldHintsEditor.h TGuiBldHintsButton.h TGuiBldGeometryFrame.h TGuiBldEditor.h TGuiBldDragManager.h TGTripleSlider.h TGTreeTable.h TGTRA.h TGToolTip.h TGToolBar.h TGTextViewStream.h TGTextView.h TGText.h TGTextEntry.h TGTextEditor.h TGTextEdit.h TGTextEditDialogs.h TGTextBuffer.h TGTableLayout.h TGTableHeader.h TGTable.h TGTableContainer.h TGTableCell.h TGTab.h TGString.h TGStatusBar.h TGSplitter.h TGSplitFrame.h TGSpeedo.h TGSlider.h TGSimpleTableInterface.h TGSimpleTable.h TGShutter.h TGShapedFrame.h TGScrollBar.h TGroupButton.h TGridResult.h TGridJobStatusList.h TGridJobStatus.h TGridJob.h TGridJDL.h TGrid.h TGridCollection.h TGResourcePool.h TGRedirectOutputGuard.h TGraphTime.h TGraphSmooth.h TGraphQQ.h TGraphPolar.h TGraphPolargram.h TGraphPainter.h TGraphMultiErrors.h TGraph.h TGraphErrors.h TGraphEditor.h TGraphDelaunay.h TGraphDelaunay2D.h TGraphBentErrors.h TGraphAsymmErrors.h TGraph2DPainter.h TGraph2D.h TGraph2DErrors.h TGProgressBar.h TGPicture.h TGPasswdDialog.h TGPack.h TGondzioSolver.h TGObject.h TGNumberEntry.h TGMsgBox.h TGMimeTypes.h TGMenu.h TGMdiMenu.h TGMdiMainFrame.h TGMdi.h TGMdiFrame.h TGMdiDecorFrame.h TGLWSIncludes.h TGLWidget.h TGLVoxelPainter.h TGLViewer.h TGLViewerEditor.h TGLViewerBase.h TGLUtil.h TGLTransManip.h TGLTH3Composition.h TGLTF3Painter.h TGLText.h TGLSurfacePainter.h TGLStopwatch.h TGLSphere.h TGLSelectRecord.h TGLSelectBuffer.h TGLScenePad.h TGLSceneInfo.h TGLScene.h TGLSceneBase.h TGLScaleManip.h TGLSAViewer.h TGLSAFrame.h TGLRotateManip.h TGLRnrCtx.h TGLQuadric.h TGLPShapeRef.h TGLPShapeObj.h TGLPShapeObjEditor.h TGLPolyMarker.h TGLPolyLine.h TGLPlotPainter.h TGLPlotCamera.h TGLPlotBox.h TGLPlot3D.h TGLPhysicalShape.h TGLPerspectiveCamera.h TGLParametric.h TGLParametricEquationGL.h TGLPadUtils.h TGLPadPainter.h TGLOverlay.h TGLOverlayButton.h TGLOutput.h TGLOrthoCamera.h TGLObject.h TGlobal.h TGLMarchingCubes.h TGLManipSet.h TGLManip.h TGLLogicalShape.h TGLLockable.h TGLLightSet.h TGLLightSetEditor.h TGLLegoPainter.h TGListView.h TGListTree.h TGListBox.h TGLIsoMesh.h TGLIncludes.h TGLHistPainter.h TGLH2PolyPainter.h TGLFormat.h TGLFontManager.h TGLFBO.h TGLFaceSet.h TGLEventHandler.h TGLEmbeddedViewer.h TGLCylinder.h TGLContext.h TGLClipSetEditor.h TGLClip.h TGLCameraOverlay.h TGLCamera.h TGLCameraGuide.h TGLBoxPainter.h TGLBoundingBox.h TGLayout.h TGLAxisPainter.h TGLAxis.h TGLAutoRotator.h TGLAnnotation.h TGLAdapter.h TGLabel.h TGL5DPainter.h TGL5D.h TGL5DDataSetEditor.h TGInputDialog.h TGImageMap.h TGIdleHandler.h TGIcon.h TGHtmlUri.h TGHtmlTokens.h TGHtml.h TGHtmlBrowser.h TGGC.h TGFSContainer.h TGFSComboBox.h TGFrame.h TGFont.h TGFontDialog.h TGFileDialog.h TGFileBrowser.h TGEventHandler.h TGeoXtru.h TGeoVoxelFinder.h TGeoVolume.h TGeoVolumeEditor.h TGeoVector3.h TGeoUniformMagField.h TGeoTypedefs.h TGeoTube.h TGeoTubeEditor.h TGeoTrd2.h TGeoTrd2Editor.h TGeoTrd1.h TGeoTrd1Editor.h TGeoTrapEditor.h TGeoTrack.h TGeoTorus.h TGeoTorusEditor.h TGeoTessellated.h TGeoTabManager.h TGeoSystemOfUnits.h TGeoStateInfo.h TGeoSphere.h TGeoSphereEditor.h TGeoShape.h TGeoShapeAssembly.h TGeoScaledShape.h TGeoRegion.h TGeoRCPtr.h TGeoPolygon.h TGeoPhysicalNode.h TGeoPhysicalConstants.h TGeoPgon.h TGeoPgonEditor.h TGeoPcon.h TGeoPconEditor.h TGeoPatternFinder.h TGeoParallelWorld.h TGeoPara.h TGeoParaEditor.h TGeoParaboloid.h TGeoPainter.h TGeoOverlap.h TGeoOpticalSurface.h TGeoNode.h TGeoNodeEditor.h TGeoNavigator.h TGeometry.h TGeoMedium.h TGeoMediumEditor.h TGeoMatrix.h TGeoMatrixEditor.h TGeoMaterial.h TGeoMaterialEditor.h TGeoManager.h TGeoManagerEditor.h TGeoHype.h TGeoHypeEditor.h TGeoHelix.h TGeoHalfSpace.h TGeoGlobalMagField.h TGeoGedFrame.h TGeoExtension.h TGeoEltu.h TGeoEltuEditor.h TGeoElement.h TGeoCone.h TGeoConeEditor.h TGeoCompositeShape.h TGeoChecker.h TGeoCache.h TGeoBuilder.h TGeoBranchArray.h TGeoBoolNode.h TGeoBBox.h TGeoBBoxEditor.h TGeoAtt.h TGeoArb8.h TGenPhaseSpace.h TGenericClassInfo.h TGenerator.h TGenCollectionStreamer.h TGenCollectionProxy.h TGedPatternSelect.h TGedMarkerSelect.h TGedFrame.h TGedEditor.h TGeant4SystemOfUnits.h TGeant4PhysicalConstants.h TGDoubleSlider.h TGDockableFrame.h TGDNDManager.h TGDMLWrite.h TGDMLParse.h TGDMLMatrix.h TGDimension.h TGCommandPlugin.h TGComboBox.h TGColorSelect.h TGColorDialog.h TGClient.h TGCanvas.h TGButton.h TGButtonGroup.h TGaxis.h TGApplication.h TG3DLine.h TFunctionTemplate.h TFunctionParametersDialog.h TFunction.h TFumiliMinimizer.h TFumili.h TFTP.h TFriendProxy.h TFriendProxyDescriptor.h TFriendElement.h TFree.h TFrame.h TFrameEditor.h TFractionFitter.h TFPBlock.h TFormula.h TFormLeafInfoReference.h TFormLeafInfo.h TFolder.h TFoamVect.h TFoamSampler.h TFoamMaxwt.h TFoamIntegrand.h TFoam.h TFoamCell.h TFitter.h TFITS.h TFitResultPtr.h TFitResult.h TFitParametersDialog.h TFitEditor.h TFileStager.h TFilePrefetch.h TFileMerger.h TFileMergeInfo.h TFileInfo.h TFile.h TFileDrawMap.h TFileCollection.h TFileCacheWrite.h TFileCacheRead.h TFFTReal.h TFFTRealComplex.h TFFTComplexReal.h TFFTComplex.h TFeldmanCousins.h TF3.h TF2.h TF2GL.h TF1NormSum.h TF1.h TF1Editor.h TF1Convolution.h TF1AbsComposition.h TF12.h TExMap.h TExec.h TException.h TEveWindowManager.h TEveWindow.h TEveWindowEditor.h TEveVSDStructs.h TEveVSD.h TEveViewerListEditor.h TEveViewer.h TEveVector.h TEveUtil.h TEveTriangleSet.h TEveTriangleSetGL.h TEveTriangleSetEditor.h TEveTreeTools.h TEveTrans.h TEveTransEditor.h TEveTrackPropagator.h TEveTrackPropagatorEditor.h TEveTrackProjected.h TEveTrackProjectedGL.h TEveTrack.h TEveTrackGL.h TEveTrackEditor.h TEveText.h TEveTextGL.h TEveTextEditor.h TEveStraightLineSet.h TEveStraightLineSetGL.h TEveStraightLineSetEditor.h TEveShape.h TEveShapeEditor.h TEveSelection.h TEveSecondarySelectable.h TEveSceneInfo.h TEveScene.h TEveScalableStraightLineSet.h TEveRGBAPaletteOverlay.h TEveRGBAPalette.h TEveRGBAPaletteEditor.h TEveQuadSet.h TEveQuadSetGL.h TEveProjections.h TEveProjectionManager.h TEveProjectionManagerEditor.h TEveProjectionBases.h TEveProjectionAxes.h TEveProjectionAxesGL.h TEveProjectionAxesEditor.h TEvePolygonSetProjected.h TEvePolygonSetProjectedGL.h TEvePointSet.h TEvePointSetArrayEditor.h TEvePlot3D.h TEvePlot3DGL.h TEvePathMark.h TEveParamList.h TEvePad.h TEventList.h TEventIter.h TEveManager.h TEveMacro.h TEveLine.h TEveLineGL.h TEveLineEditor.h TEveLegoEventHandler.h TEveJetCone.h TEveJetConeGL.h TEveJetConeEditor.h TEveGValuators.h TEveGridStepper.h TEveGridStepperEditor.h TEveGeoShape.h TEveGeoShapeExtract.h TEveGeoPolyShape.h TEveGeoNode.h TEveGeoNodeEditor.h TEveGedEditor.h TEveFrameBox.h TEveFrameBoxGL.h TEveEventManager.h TEveElement.h TEveElementEditor.h TEveDigitSet.h TEveDigitSetGL.h TEveDigitSetEditor.h TEveCompound.h TEveChunkManager.h TEveCaloVizEditor.h TEveCaloLegoOverlay.h TEveCaloLegoGL.h TEveCaloLegoEditor.h TEveCalo.h TEveCaloData.h TEveCalo3DGL.h TEveCalo2DGL.h TEveBrowser.h TEveBoxSet.h TEveBoxSetGL.h TEveBox.h TEveBoxGL.h TEveArrow.h TEveArrowGL.h TEveArrowEditor.h TError.h TEnv.h TEnum.h TEnumConstant.h TEntryList.h TEntryListFromFile.h TEntryListBlock.h TEntryListArray.h TEmulatedMapProxy.h TEmulatedCollectionProxy.h TELTU.h TEllipse.h TEfficiency.h TDSetProxy.h TDSet.h TDrawFeedback.h TDOMParser.h TDocParser.h TDocOutput.h TDocInfo.h TDocDirective.h TDirectory.h TDirectoryFile.h TDictionary.h TDictAttributeMap.h TDiamond.h TDialogCanvas.h TDecompSVD.h TDecompSparse.h TDecompQRH.h TDecompLU.h TDecompChol.h TDecompBK.h TDecompBase.h TDecayChannel.h TDavixSystem.h TDavixFile.h TDatime.h TDataType.h TDataSetManager.h TDataSetManagerFile.h TDataSetManagerAliEn.h TDataMember.h TDatabasePDG.h TCut.h TCutG.h TCurlyLine.h TCurlyLineEditor.h TCurlyArc.h TCurlyArcEditor.h TCTUB.h TCrown.h TCreatePrimitives.h TControlBarImp.h TControlBar.h TControlBarButton.h TContextMenuImp.h TContextMenu.h TContainerConverters.h TCONS.h TConfidenceLevel.h TCONE.h TCondor.h TConditionImp.h TCondition.h TComplex.h TColorWheel.h TColor.h TColorGradient.h TCollectionProxyInfo.h TCollectionProxyFactory.h TCollection.h TClonesArray.h TClassTree.h TClassTable.h TClassStreamer.h TClassRef.h TClassMenuItem.h TClass.h TClassGenerator.h TClassEdit.h TClassDocOutput.h TChainIndex.h TChain.h TChainElement.h TCanvasImp.h TCanvas.h TCandle.h TButton.h TBufferXML.h TBufferText.h TBufferSQL.h TBufferSQL2.h TBufferJSON.h TBufferIO.h TBuffer.h TBufferFile.h TBuffer3DTypes.h TBuffer3D.h TBtree.h TBrowserImp.h TBrowser.h TBRIK.h TBranchSTL.h TBranchRef.h TBranchProxyTemplate.h TBranchProxy.h TBranchProxyDirector.h TBranchProxyDescriptor.h TBranchProxyClassDescriptor.h TBranchObject.h TBranch.h TBranchElement.h TBranchClones.h TBranchCacheInfo.h TBranchBrowsable.h TBox.h TBits.h TBinomialEfficiencyFitter.h TBenchmark.h TBasketSQL.h TBasket.h TBaseClass.h TBase64.h TBackCompFitter.h TAxisModLab.h TAxis.h TAxisEditor.h TAxis3D.h TAuthenticate.h TAttText.h TAttTextEditor.h TAttParticle.h TAttPad.h TAttMarker.h TAttMarkerEditor.h TAttLine.h TAttLineEditor.h TAttImage.h TAttFill.h TAttFillEditor.h TAttCanvas.h TAttBBox.h TAttBBox2D.h TAttAxis.h TAtt3D.h TAtomicCountPthread.h TAtomicCount.h TAtomicCountGcc.h TASPluginGS.h TASPaletteEditor.h TASImagePlugin.h TASImage.h TArrow.h TArrowEditor.h TArrayS.h TArrayL.h TArrayL64.h TArrayI.h TArray.h TArrayF.h TArrayD.h TArrayC.h TArchiveFile.h TArc.h TArcBall.h TApplicationServer.h TApplicationRemote.h TApplicationImp.h TApplication.h TAdvancedGraphicsDialog.h Strlen.h strlcpy.h snprintf.h RZip.h RVersion.h RtypesImp.h Rtypes.h RtypesCore.h Rstrstream.h RStringView.h RStipples.h RRemoteProtocol.h RQ_OBJECT.h Rpair.h RooXYChi2Var.h RooWrapperPdf.h RooWorkspaceHandle.h RooWorkspace.h RooVoigtian.h RooVectorDataStore.h RooVDTHeaders.h RooUnitTest.h RooUniform.h RooUniformBinning.h RooUnblindUniform.h RooUnblindPrecision.h RooUnblindOffset.h RooUnblindCPAsymVar.h root_std_complex.h RooTruthModel.h RooTreeDataStore.h RooTreeData.h RooTrace.h RooTObjWrap.h RootMetaSelection.h RooTMathReg.h RooThresholdCategory.h RooTFoamBinding.h RooTFnPdfBinding.h RooTFnBinding.h RooTemplateProxy.h RooTable.h RooSuperCategory.h RooStudyPackage.h RooStudyManager.h RooStringVar.h RooStreamParser.h RooSTLRefCountList.h RooStepFunction.h RooSpHarmonic.h RooSpan.h RooSimWSTool.h RooSimultaneous.h RooSimSplitGenContext.h RooSimPdfBuilder.h RooSimGenContext.h RooSharedProperties.h RooSetProxy.h RooSetPair.h RooSentinel.h RooSegmentedIntegrator2D.h RooSegmentedIntegrator1D.h RooSecondMoment.h RooScaledFunc.h RooResolutionModel.h RooRefCountList.h RooRecursiveFraction.h RooRealVarSharedProperties.h RooRealVar.h RooRealSumPdf.h RooRealSumFunc.h RooRealProxy.h RooRealMPFE.h RooRealIntegral.h RooRealConstant.h RooRealBinding.h RooRealAnalytic.h RooRangeBoolean.h RooRangeBinning.h RooRandomizeParamMCSModule.h RooRandom.h RooQuasiRandomGenerator.h RooPullVar.h RooProofDriverSelector.h RooProjectedPdf.h RooProfileLL.h RooProduct.h RooProdPdf.h RooProdGenContext.h RooPrintable.h RooPolyVar.h RooPolynomial.h RooPoisson.h RooPlot.h RooPlotable.h RooParamHistFunc.h RooParametricStepFunction.h RooParamBinning.h RooObjCacheManager.h RooNumRunningInt.h RooNumIntFactory.h RooNumIntConfig.h RooNumGenFactory.h RooNumGenConfig.h RooNumConvPdf.h RooNumConvolution.h RooNumCdf.h RooNumber.h RooNovosibirsk.h RooNormSetCache.h RooNonCPEigenDecay.h RooNonCentralChiSquare.h RooNLLVar.h RooNDKeysPdf.h RooNameSet.h RooNameReg.h RooMultiVarGaussian.h RooMultiGenFunction.h RooMultiCategory.h RooMultiBinomial.h RooMsgService.h RooMPSentinel.h RooMomentMorphND.h RooMomentMorph.h RooMomentMorphFuncND.h RooMomentMorphFunc.h RooMoment.h RooMinuit.h RooMinimizer.h RooMinimizerFcn.h RooMCStudy.h RooMCIntegrator.h RooMathMoreReg.h RooMath.h RooMathCoreReg.h RooMappedCategory.h RooLognormal.h RooListProxy.h RooList.h RooLinTransBinning.h RooLinkedListIter.h RooLinkedList.h RooLinkedListElem.h RooLinearVar.h RooLegendre.h RooLandau.h RooKeysPdf.h RooJohnson.h RooJeffreysPrior.h RooInvTransform.h RooInt.h RooIntegratorBinding.h RooIntegrator2D.h RooIntegrator1D.h RooIntegralMorph.h RooImproperIntegrator1D.h RooHypatia2.h RooHistPdf.h RooHist.h RooHistFunc.h RooHistError.h RooHistConstraint.h RooHelpers.h RooHashTable.h RooGrid.h RooGlobalFunc.h RooGExpModel.h RooGenProdProj.h RooGenFunction.h RooGenFitStudy.h RooGenericPdf.h RooGenContext.h RooGaussModel.h RooGaussKronrodIntegrator1D.h RooGaussian.h RooGamma.h RooFunctor.h RooFunctorBinding.h RooFunctor1DBinding.h RooFracRemainder.h RooFormulaVar.h RooFormula.h RooFoamGenerator.h RooFitResult.h RooFitMoreLib.h RooFit.h RooFirstMoment.h RooFFTConvPdf.h RooFactoryWSTool.h RooExtendPdf.h RooExtendedTerm.h RooExtendedBinding.h RooExponential.h RooExpensiveObjectCache.h RooErrorVar.h RooErrorHandler.h RooEllipse.h RooEffProd.h RooEfficiency.h RooEffGenContext.h RooDstD0BG.h RooDouble.h RooDLLSignificanceMCSModule.h RooDirItem.h RooDerivative.h RooDecay.h RooDataWeightedAverage.h RooDataSet.h RooDataProjBinding.h RooDataHistSliceIter.h RooDataHist.h RooCustomizer.h RooCurve.h RooConvIntegrandBinding.h RooConvGenContext.h RooConvCoefVar.h RooConstVar.h RooConstraintSum.h RooCompositeDataStore.h RooCmdConfig.h RooCmdArg.h RooClassFactory.h RooChiSquarePdf.h RooChi2Var.h RooChi2MCSModule.h RooChebychev.h RooChangeTracker.h RooCFunction4Binding.h RooCFunction3Binding.h RooCFunction2Binding.h RooCFunction1Binding.h RooCBShape.h RooCatType.h RooCategoryProxy.h RooCategory.h RooCacheManager.h RooCachedReal.h RooCachedPdf.h RooBukinPdf.h RooBrentRootFinder.h RooBreitWigner.h RooBMixDecay.h RooBlindTools.h RooBinning.h RooBinningCategory.h RooBinnedGenContext.h RooBinIntegrator.h RooBifurGauss.h RooBernstein.h RooBDecay.h RooBCPGenDecay.h RooBCPEffDecay.h RooBanner.h RooArgusBG.h RooArgSet.h RooArgProxy.h RooArgList.h RooAICRegistry.h RooAddPdf.h RooAddModel.h RooAddition.h RooAddGenContext.h RooAdaptiveIntegratorND.h RooAdaptiveGaussKronrodIntegrator1D.h RooAcceptReject.h RooAbsTestStatistic.h RooAbsStudy.h RooAbsString.h RooAbsSelfCachedReal.h RooAbsSelfCachedPdf.h RooAbsRootFinder.h RooAbsRealLValue.h RooAbsReal.h RooAbsProxy.h RooAbsPdf.h RooAbsOptTestStatistic.h RooAbsNumGenerator.h RooAbsMoment.h RooAbsMCStudyModule.h RooAbsLValue.h RooAbsIntegrator.h RooAbsHiddenReal.h RooAbsGenContext.h RooAbsFunc.h RooAbsDataStore.h RooAbsData.h RooAbsCollection.h RooAbsCategoryLValue.h RooAbsCategory.h RooAbsCache.h RooAbsCacheElement.h RooAbsCachedReal.h RooAbsCachedPdf.h RooAbsBinning.h RooAbsArg.h RooAbsAnaConvPdf.h Roo2DKeysPdf.h Roo1DTable.h Riostream.h RConfig.h PosixThreadInc.h PoolUtils.h NetErrors.h MPSendRecv.h MPCode.h MessageTypes.h MemCheck.h Match.h KeySymbols.h Htypes.h Hparam.h Hoption.h HFMsgService.h HFitInterface.h Hepevt.h HelpTextTV.h HelpText.h HelpSMText.h GuiTypes.h Gtypes.h GLConstants.h Getline.h FTVectoriser.h FTVector.h FTTextureGlyph.h FTSize.h FTPolyGlyph.h FTPoint.h FTPixmapGlyph.h FTOutlineGlyph.h FTList.h FTLibrary.h FTGlyph.h FTGlyphContainer.h FTGLTextureFont.h FTGLPolygonFont.h FTGLPixmapFont.h FTGLOutlineFont.h FTGL.h FTGLExtrdFont.h FTGLBitmapFont.h FTFont.h FTFace.h FTExtrdGlyph.h FTContour.h FTCharToGlyphIndexMap.h FTCharmap.h FTBitmapGlyph.h FTBBox.h Foption.h ESTLType.h DllImport.h CsgOps.h Compression.h cfortran.h Byteswap.h Bytes.h Buttons.h Bswapcpy.h BatchHelpers.h BatchData.h AuthConst.h RConfigure.h RConfigOptions.h compiledata.h module.modulemap XrdVersion.hh RGitCommit.h XrdSfs XProtocol XrdXml XrdCms XrdXrootd XrdHttp XrdAcc Xrd private XrdOfs XrdOuc XrdClient XrdPosix XrdCks XrdSys XrdOss XrdCl XrdNet XrdSec XrdFileCache Fit v5 Math ROOT CPyCppyy TMVA RooFitLegacy RooStats; do
		if [ -e "$each" ]; then
			sudo mv $each junk/
		fi
	done
	#ls -lart
	sudo rm -rf junk
	echo "...done"
fi


# from https://root.cern/install/
# git clone --branch latest-stable --depth=1 https://github.com/root-project/root.git root_src
# mkdir root_build root_install && cd root_build
# cmake -DCMAKE_INSTALL_PREFIX=../root_install ../root_src # && check cmake configuration output for warnings or errors
# cmake --build . -- install -j4 # if you have 4 cores available for compilation
# source ../root_install/bin/thisroot.sh # or thisroot.{fish,csh}

cd
mkdir -p build
cd build
mkdir -p root
cd root
if [ ! -e root_src ]; then
	git clone --branch latest-stable --depth=1 https://github.com/root-project/root.git root_src
else
	cd root_src
	git pull
	cd ..
fi
mkdir -p root_build
cd root_build
cmake -DCMAKE_INSTALL_PREFIX=/usr/local ../root_src
cmake --build . -j$j
sudo cmake --build . -- install

# list of things that get installed in /usr/local:
# geant4.sh geant4.csh geant4-config LICENSE man geom lib include emacs config bin README etc fonts macros icons ui5 js tutorials cmake

#if [ ! -e $build/$dirname ]; then
#	if [ ! -e $filename ]; then
#		declare url="https://root.cern/download/$filename"
#		wget $url
#	fi
#	tar xzf $filename
#fi

#cd $build/$dirname
#if [ -e obj ]; then
#	rm -rf obj
#fi
#if [ ! -e obj ]; then
#	mkdir obj
#	cd obj
#	cmake ..
#else
#	cd obj
#fi
#time nice make -j$j
#sudo nice make install
#sudo find /usr/local/etc -type d -exec chmod --changes 755 {} \; -o -type f -exec chmod --changes 644 {} \;

cat <<DOC

to test your installation:

. /usr/local/bin/thisroot.sh
root
.q

python2
import ROOT
ctrl-d

python3
import ROOT
ctrl-d
DOC

