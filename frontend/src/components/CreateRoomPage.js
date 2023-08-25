// this is used to store the Page which is used to display the page to join from the code of the main application
import React , {Component} from "react";
import Button from "@material-ui/core/Button";
import Grid from "@material-ui/core/Grid";
import { Typography } from "@material-ui/core";
import TextField from "@material-ui/core/TextField";
import FormHelperText from "@material-ui/core/FormHelperText";
import FormControl from "@material-ui/core/FormControl";
import { Link } from "react-router-dom";
import Radio from "@material-ui/core/Radio";
import RadioGroup from "@material-ui/core/RadioGroup";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import { Collapse } from "@material-ui/core";
import Alert from "@material-ui/lab/Alert";


export default class CreateRoomPage extends React.Component{
  static defaultProps = {
    votesToSkip: 2,
    guestCanPause: true,
    update: false,
    roomCode: null,
    updateCallback: () => {},
  };

    constructor(props){
        super(props);
        // we are going to put some default states
        // whenever we are going to change the state of the application, it automatically updates ans rerenders
        this.state = {
          guestCanPause: this.props.guestCanPause,
          votesToSkip: this.props.votesToSkip,
          errorMsg: "",
          successMsg: "",
        };
        console.log("hello world");
        this.handleUpdateButtonPressed=this.handleUpdateButtonPressed.bind(this);
        this.handleVotesChange = this.handleVotesChange.bind(this);
        this.handleGuestCanPauseChange = this.handleGuestCanPauseChange.bind(this);
        this.handleRoomButtonPressed = this.handleRoomButtonPressed.bind(this);
    }
    // e is the object that calls the function
    handleVotesChange(e){
        this.setState({
            votesToSkip: e.target.value,
        });
        
    }

    handleGuestCanPauseChange(e){
            this.setState({
                guestCanPause: e.target.value === "true" ? true : false 
            })
    }
      // this will create an endpoint to link this to the API backend and create a request
      // which will allow us to create a new room with the information which is used in the form
      // after this is done we need to access the code generated and then go the webpage using the code
      // will allow the users to join the room and allow the play the media player
    handleRoomButtonPressed(){
        const requestOptions = {
            method:"POST",
            headers: {"Content-Type": "application/json"},
            //JSON.stringify convert javascript objects into strings.
            // when the data is sent to the web server, the data has to be a string thus we convert it
            body: JSON.stringify({
              votes_to_skip : this.state.votesToSkip,
              guest_can_pause : this.state.guestCanPause,
            }),
        };
        fetch("/api/create-room",requestOptions)
        .then((response) => response.json())
        .then((data)=> this.props.history.push("/room/"+ data.code));
    }

    handleUpdateButtonPressed(){
      const requestOptions = {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          votes_to_skip: this.state.votesToSkip,
          guest_can_pause: this.state.guestCanPause,
          code: this.props.roomCode,
        }),
      };
      fetch("/api/update-room", requestOptions).then((response) => {
        if (response.ok) {
          this.setState({
            successMsg: "Room updated successfully!",
          });
        } else {
          this.setState({
            errorMsg: "Error updating room...",
          });
        }
        this.props.updateCallback();
      });
        // this might create a problem as the before fetch may not be complete executing before we call the .then 
        // this.updateCallback()
    }

    renderUpdateButtons(){
      return(
        <Grid item xs={12} align = "center">
          <Button
          color = "primary"
          variant = "contained"
          onClick = {this.handleUpdateButtonPressed}>
          Update Room
          </Button>
        </Grid>
      );
    }


    renderCreateButtons(){
      return (
      <Grid container spacing={1}>
          <Grid item xs={12} align = "center">
          <Button
          color = "primary"
          variant = "contained"
          onClick = {this.handleRoomButtonPressed}>
          Create A Room
          </Button>
          </Grid>
          <Grid item xs={12} align="center">
          <Button color="secondary" variant="contained" to="/" component={Link}>
          Go Back
          </Button>
          </Grid>
      </Grid>
      );
    }
    
    render(){
      const title = this.props.update ? "Update Room" : "Create a Room" 
        return( 
        <Grid container spacing={1}>
             <Grid item xs={12} align="center">
             <Collapse in={ this.state.errorMsg != '' || this.state.successMsg!= ''}>
                {this.state.successMsg != ' ' ? 
                  (<Alert severity="success" onClose={ () => {
                    this.setState({ successMsg : "" });
                  }}
                  > 
                  {this.state.successMsg}
                  </Alert>)
                  :
                  (<Alert severity="error" onClose={()=>{
                    this.setState({errorMsg:""});
                  }}
                  >
                  {this.state.errorMsg}
                  </Alert>)
                }
             </Collapse>
            </Grid>
            
            <Grid item xs={12} align="center">
              <Typography component="h4" variant="h4">
                {title}
              </Typography>
            </Grid>
            
            <Grid item xs={12} align="center">
              <FormControl component="fieldset">
                <FormHelperText>
                  <div align="center"> Guest Control of Playback State </div>
                </FormHelperText>
                <RadioGroup
                  row
                  defaultValue = {this.props.guestCanPause.toString()}
                  onChange = {this.handleGuestCanPauseChange}
                >
                  <FormControlLabel
                    value="true"
                    control = {<Radio color="primary" />}
                    label= "Play/Pause"
                    labelPlacement = "bottom"
                  />

                  <FormControlLabel
                    value="false"
                    control={<Radio color="secondary" />}
                    label = "No Control"
                    labelPlacement="bottom"
                  />
                </RadioGroup>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} align="center">
              <FormControl>
                <TextField
                  required={true}
                  type="number"
                  onChange = {this.handleVotesChange}
                  defaultValue = {this.state.votesToSkip}
                  inputProps = {{
                    min: 1,
                    style: { textAlign: "center" },
                  }}
                />
                <FormHelperText>
                  <div align="center">Votes Required To Skip Song</div>
                </FormHelperText>
              </FormControl>
            </Grid>
            {this.props.update ? this.renderUpdateButtons(): this.renderCreateButtons()}
          </Grid>
        
        );
    }
}