<?php

class Database{
    public function getConnection(){
        $dbConnect = new PDO("
        mysql:
        host=us-cdbr-east-02.cleardb.com;port=3306;dbname=heroku_594ae4223a52c95",
        "b263072c1ab18d","e4aaaba1");
        return $dbConnect;
    }
}
?>