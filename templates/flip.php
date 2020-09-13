<?php 

include './database.php';
include './clubs.php';

$clubs = new Clubs();
$clubs->abbr = $_GET["id"];
$club = $clubs->getOneTeam();
$name = $clubs->getFullName();
$full = $name['Team'];
    
$posi = array('Goalkeeper #1','Goalkeeper #2','Defender #1','Defender #2','Defender #3'
,'Defender #4','Defender #5','Defender #6','Midfielder #1','Midfielder #2'
,'Midfielder #3','Midfielder #4','Midfielder #5','Attacker #1','Attacker #2'
,'Attacker #3','Attacker #4','Attacker #5')
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?=$full?></title>
    <style>
        .scene{
            width: 420px;
            height: 840px;
            perspective: 840px;
        }
        h3{
            font-family:"Calibri";
            font-style: bold;
            padding-left: 40px;
            padding-top: 30px;
            font-size: 160px;
            margin: 0;
        }
        .card0, .card1, .card2, .card3,
        .card4, .card5, .card6, .card7,
        .card8, .card9, .card10, .card11,
        .card12, .card13, .card14, .card15,
        .card16, .card17{
            height: 100%;
            width: 100%;
            position: relative;
            transition: transform 3s;
            transform-style: preserve-3d;
            left:100%;
        }
        .card_face{
            position:absolute;
            height: 100%;
            width: 100%;
            backface-visibility: hidden;
        }
        .card_face--front{
        }
        .card_face--back{
            transform: rotateY(180deg);
        }
        .card0.is-flipped, .card1.is-flipped,
        .card2.is-flipped, .card3.is-flipped,
        .card4.is-flipped, .card5.is-flipped, 
        .card6.is-flipped, .card7.is-flipped,
        .card8.is-flipped, .card9.is-flipped, 
        .card10.is-flipped, .card11.is-flipped,
        .card12.is-flipped, .card13.is-flipped, 
        .card14.is-flipped, .card15.is-flipped,
        .card16.is-flipped, .card17.is-flipped{
            transform: rotateY(-180deg);
        }
        .summary{
            width: 110px;
            height: auto;
            display: inline-block;
            margin-left: 8px;
            margin-right: 12px;
        }
        .flex{
            display: flex;
            flex-direction: row;
            justify-content: center;
            padding-top: 6px;
            padding-bottom: 6px;
        }
        .team{
            position:fixed;
            right:30px;
            top:30px;
        }
        .home{
            position:fixed;
            right:30px;
            top:90px;
        }
        h1{
        padding-left: 40px;
        padding-top: 20px;
        }
    </style>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
</head>
<body>


    <h1><?=$full?></h1>
    <button class="btn btn-outline-dark btn-lg team" id="team"><?=$full?></button>    
    <a href="./index.php" class="btn btn-outline-success btn-lg home" >Home</a>
    <?php foreach($club as $index=>$player):?>
    <h3><?=$posi[$index]?></h3>
    <div class="scene">
        <div class=<?="card".$index?>>
            <div class="card_face card_face--front">
                <img src = "Card Back.jpg" width="420px" height=auto>
            </div>
            <div class="card_face card_face--back">
                <img src = "./Cards./投影片<?=$player['Pick']?>.JPG" width="400px" height=auto>
            </div>
        </div>
    </div>
    <?php endforeach?>
    <div style="display: block; padding-top:1000px; padding-bottom: 40px;">
    <div class="flex">
        <img src = "./Cards./投影片<?=$club[0]['Pick']?>.JPG" class="summary">
        <img src = "./Cards./投影片<?=$club[1]['Pick']?>.JPG" class="summary">
    </div>
        <div class="flex">
            <img src = "./Cards./投影片<?=$club[2]['Pick']?>.JPG" class="summary">
            <img src = "./Cards./投影片<?=$club[3]['Pick']?>.JPG" class="summary">
            <img src = "./Cards./投影片<?=$club[4]['Pick']?>.JPG" class="summary">
            <img src = "./Cards./投影片<?=$club[5]['Pick']?>.JPG" class="summary">
            <img src = "./Cards./投影片<?=$club[6]['Pick']?>.JPG" class="summary">
            <img src = "./Cards./投影片<?=$club[7]['Pick']?>.JPG" class="summary">       
        </div>
        <div class="flex">
            <img src = "./Cards./投影片<?=$club[8]['Pick']?>.JPG" class="summary">
            <img src = "./Cards./投影片<?=$club[9]['Pick']?>.JPG" class="summary">
            <img src = "./Cards./投影片<?=$club[10]['Pick']?>.JPG" class="summary">
            <img src = "./Cards./投影片<?=$club[11]['Pick']?>.JPG" class="summary">
            <img src = "./Cards./投影片<?=$club[12]['Pick']?>.JPG" class="summary">  
        </div>
        <div class="flex">
            <img src = "./Cards./投影片<?=$club[13]['Pick']?>.JPG" class="summary">
            <img src = "./Cards./投影片<?=$club[14]['Pick']?>.JPG" class="summary">
            <img src = "./Cards./投影片<?=$club[15]['Pick']?>.JPG" class="summary">
            <img src = "./Cards./投影片<?=$club[16]['Pick']?>.JPG" class="summary">
            <img src = "./Cards./投影片<?=$club[17]['Pick']?>.JPG" class="summary">  
        </div>
    </div>
    </div>
    <script>
        var A = document.querySelector('.card0');
        A.addEventListener( 'click', function() {
            A.classList.toggle('is-flipped');
        });
        var B = document.querySelector('.card1');
        B.addEventListener( 'click', function() {
            B.classList.toggle('is-flipped');
        });
        var C = document.querySelector('.card2');
        C.addEventListener( 'click', function() {
            C.classList.toggle('is-flipped');
        });
        var D = document.querySelector('.card3');
        D.addEventListener( 'click', function() {
            D.classList.toggle('is-flipped');
        });
        var E = document.querySelector('.card4');
        E.addEventListener( 'click', function() {
            E.classList.toggle('is-flipped');
        });
        var F = document.querySelector('.card5');
        F.addEventListener( 'click', function() {
            F.classList.toggle('is-flipped');
        });
        var G = document.querySelector('.card6');
        G.addEventListener( 'click', function() {
            G.classList.toggle('is-flipped');
        });
        var H = document.querySelector('.card7');
        H.addEventListener( 'click', function() {
            H.classList.toggle('is-flipped');
        });
        var I = document.querySelector('.card8');
        I.addEventListener( 'click', function() {
            I.classList.toggle('is-flipped');
        });
        var J = document.querySelector('.card9');
        J.addEventListener( 'click', function() {
            J.classList.toggle('is-flipped');
        });
        var K = document.querySelector('.card10');
        K.addEventListener( 'click', function() {
            K.classList.toggle('is-flipped');
        });
        var L = document.querySelector('.card11');
        L.addEventListener( 'click', function() {
            L.classList.toggle('is-flipped');
        });
        var M = document.querySelector('.card12');
        M.addEventListener( 'click', function() {
            M.classList.toggle('is-flipped');
        });
        var N = document.querySelector('.card13');
        N.addEventListener( 'click', function() {
            N.classList.toggle('is-flipped');
        });
        var O = document.querySelector('.card14');
        O.addEventListener( 'click', function() {
            O.classList.toggle('is-flipped');
        });
        var P = document.querySelector('.card15');
        P.addEventListener( 'click', function() {
            P.classList.toggle('is-flipped');
        });
        var Q = document.querySelector('.card16');
        Q.addEventListener( 'click', function() {
            Q.classList.toggle('is-flipped');
        });
        var R = document.querySelector('.card17');
        R.addEventListener( 'click', function() {
            R.classList.toggle('is-flipped');
        });
        function showSquad() {
            var x = document.getElementById("squad");
            if (x.style.display === "none") {
                x.style.display = "block";
            } else {
                x.style.display = "none";
            }
            }
            $("#team").click(function() {
            $("html, body").animate({ scrollTop: $(document).height() }, "slow");
            return false;
            });​
    </script>
</body>
</html>