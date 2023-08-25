// this is used to store the homepage of the main application
import React, { Component } from "react";
import RoomJoinPage from "./RoomJoinPage";
import CreateRoomPage from "./CreateRoomPage";
import { Grid, Button, ButtonGroup, Typography } from "@material-ui/core";
import Room from "./Room";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
  Redirect,
} from "react-router-dom";
import Info from "./Info";

export default class Homepage extends React.Component {
    constructor(props){
        super(props);
        this.state={
            roomCode : null,
        }
        this.clearRoomCode=this.clearRoomCode.bind(this);
    }

    async componentDidMount(){
        // if the room code is returned as it has a session running, 
        // the fetch returns the response which is the json format,
        // after the data is json object which is then returned. 
        fetch("/api/user-in-room")
        .then((response)=> response.json())
        .then((data)=> {
            this.setState({
            roomCode: data.code
        });
     });
    } 

    renderHomePage(){
        return(
            <Grid container spacing={3}>
                <Grid item xs={12} align="center">
                    <Typography variant="h4" compact="h4">
                        Welcome to House Party !!!
                    </Typography>
                </Grid>
                <Grid item xs={12} align="center">
                    <ButtonGroup variant="contained" color="primary">
                        <Button color="primary" to="/join" component={Link}>
                            Join a Room
                        </Button>
                        <Button color="default" to="/info" component={Link}>
                            Info
                        </Button>
                        <Button color="secondary" to="/create" component={Link}>
                            Create a Room
                        </Button>
                    </ButtonGroup>
                </Grid>
            </Grid>
        );
    }

    clearRoomCode(){
        this.setState({
            roomCode:null,
        })
    }
    
    render() {
        return (
            <Router>
                <Switch>
                    {/* if we have the room code we render the page which has the code or we render the homepage. */}
                    <Route 
                        exact  
                        path="/" 
                        render = {() => {
                        return this.state.roomCode ? (
                        <Redirect to = {`/room/${this.state.roomCode}`}/> 
                        ) : (
                            this.renderHomePage()
                            );
                        }}></Route>
                     <Route path="/join" component={RoomJoinPage} />
          <Route path="/info" component={Info} />
          <Route path="/create" component={CreateRoomPage} />
          <Route
            path="/room/:roomCode"
            render={(props) => {
              return <Room {...props} leaveRoomCallback={this.clearRoomCode} />;
            }}
          />
                </Switch>
            </Router>
        );
    }
}