import React, { Component } from 'react';
import './App.css';
import twineFile from '../../Stuffed.html';
import LeftSideBar from './LeftSideBar';
import RightSideBar from './RightSideBar';
import IntroScreen from './IntroScreen';
import GirlSvgTest from './GirlSvgTest';
import Header from './Header';

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      showingIntroScreen: true,
      debugMode: false
    };
    this.needToAttachHarlowe = true;
    window.harloweUpdate = this.harloweUpdate.bind(this);
    this.script = document.createElement("script");
    this.script.src = "harlowe-min.js";
    this.script.async = true;
    const data = document.createElement("div");
    data.innerHTML = twineFile;
    document.body.appendChild(data);
  }

  componentDidUpdate() {
    if(!this.props.showingIntroScreen && this.needToAttachHarlowe) {
      console.log("attaching harlowe");
      this.needToAttachHarlowe = false;
      document.body.appendChild(this.script);
    }
  }

  setDebugMode(debugMode) {
    this.setState({debugMode});
  }

  setDebugTooltips(debugTooltips) {
    this.setState({debugTooltips});
    window.setDebugTooltips(debugTooltips);
  }

  showIntro() {
    this.setState({showingIntroScreen: true});
  }

  hideIntro() {
    this.setState({showingIntroScreen: false});
    this.needToAttachHarlowe = true;
  }

  startGame(path) {
    this.hideIntro();
    window.reactTwineStartPath = path;
  }

  harloweUpdate() {
    const x = window._state.variables;
    var map = {};
    for (let key in x) { //eslint-disable-line
      map[key] = x[key]; /* We need to search the __proto__ etc for many layers down.  Each __proto__ points to a past state */
    }
    console.log("harloweUpdate");
    this.setState(map);
  }

  render() {
    if (location.pathname === "/girl" || location.pathname === "/boy" || location.search === "?girl" || location.search === "?boy")
      return <GirlSvgTest />
    if (this.state.showingIntroScreen)
      return <IntroScreen callbackStartGame={path => this.startGame(path)}/>
    return (
      <div className={"App " + (this.state.debugMode?"debug-mode" : "")}>
        <Header harlowe={this.state}/>
        <RightSideBar callbackSetDebugMode={this.setDebugMode.bind(this)} callbackSetDebugTooltips={this.setDebugTooltips.bind(this)} debugTooltips={this.state.debugTooltips} debugMode={this.state.debugMode} />
        <LeftSideBar harlowe={this.state}/>
        <main id="center">
          <tw-story dangerouslySetInnerHTML={{__html: ""}}></tw-story>
        </main>

        {/*<div id="footer-wrapper">
          <footer id="footer"><p></p></footer>
        </div>*/}
      </div>
    );
  }
}

export default App;
