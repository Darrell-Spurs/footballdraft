<?php
class Clubs{
    include "./database.php";
    public $dbConnect;
    public $owner;
    public $abbr;
    public $team;
    public $coach;
    
    public function __construct(){
        $db = new Database();
        $this->dbConnect = $db->getConnection();
    }

    public function getAllTeams(){
        $sql = "SELECT * FROM league_teams";
        $getData = $this->dbConnect->prepare($sql);
        $getData->execute();
        $data = $getData->fetchAll(PDO::FETCH_ASSOC);
        return $data;
    }
    public function getAllPlayers(){
        $sql = "SELECT * FROM all_players"
        $getData = $this->$dbConnect->prepare($sql);
        $getData->execute();
        $data = $getData->fetch(PDO:FETCH_ASSOC);
        return $data;
    }

    public function getOneTeam(){
        $sql = "SELECT * FROM random_team WHERE Team = :team
        AND(POSITION = 'GK')";
        $getTeam = $this->dbConnect->prepare($sql);
        $getTeam->bindParam(":team",$this->abbr);
        $getTeam->execute();
        $gk = $getTeam->fetchAll(PDO::FETCH_ASSOC);


        $sql = "SELECT * FROM random_team WHERE Team = :team
        AND(POSITION = 'LB' OR POSITION = 'CB' OR POSITION = 'RB')";
        $getTeam = $this->dbConnect->prepare($sql);
        $getTeam->bindParam(":team",$this->abbr);
        $getTeam->execute();
        $df = $getTeam->fetchAll(PDO::FETCH_ASSOC);
        
        $sql = "SELECT * FROM random_team WHERE Team = :team
        AND(POSITION = 'CM' OR POSITION = 'CDM' OR POSITION = 'CAM')";
        $getTeam = $this->dbConnect->prepare($sql);
        $getTeam->bindParam(":team",$this->abbr);
        $getTeam->execute();
        $md = $getTeam->fetchAll(PDO::FETCH_ASSOC);

        $sql = "SELECT * FROM random_team WHERE Team = :team
        AND(POSITION = 'RW' OR POSITION = 'LW' OR POSITION = 'ST')";
        $getTeam = $this->dbConnect->prepare($sql);
        $getTeam->bindParam(":team",$this->abbr);
        $getTeam->execute();
        $fw = $getTeam->fetchAll(PDO::FETCH_ASSOC);

        $data = array_merge($gk,$df,$md,$fw);
        return $data;
    }

    public function getFullName(){
        $sql = "SELECT Team FROM league_teams WHERE Abbreviation=:abbr;";
        $getData = $this->dbConnect->prepare($sql);
        $getData->bindParam(":abbr",$this->abbr);
        $getData->execute();
        $data = $getData->fetch(PDO::FETCH_ASSOC);
        return $data;
    }

}
?>