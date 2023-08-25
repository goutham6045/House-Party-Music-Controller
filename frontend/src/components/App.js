import React , { Component } from "react";
import {render} from "react-dom";
import Homepage from "./Homepage";
import { createRoot } from 'react-dom/client';

export default class App extends Component{
    constructor(props){
        super(props);
            // store all the stateful aspects we want to store and whenever the state of the database is changed then it automatically 
            //rerenders the changed component according to the changes that has been made in the database
    }
    render(){
        // return <h1>Testingg React Code</h1>
        //we create another component and then render that components matter in this app component
        return (
         <div className ='center'>
            <Homepage />
         </div>
        );
    }
}
const appDiv = document.getElementById("app");

createRoot(appDiv).render(<App />);

// we render this component inside of the index.html div tag which has the id tag named as app
// we get the element id using document.getelementbyid and then render the contents of the app.js

// we have to click on the urls to redirect us to the webpages of each component. REACT router aspect is now 