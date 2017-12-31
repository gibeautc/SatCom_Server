<?php

	echo "<html>";
	echo '<head><style>table, th, td {border: 1px solid black;}</style><meta http-equiv="refresh" content="30" > </head><body>';
	$servername="localhost";
	$username="root";
	$password="aq12ws";
	$dbname="weather";
	$conn= new mysqli($servername,$username,$password,$dbname);
	if($conn->connect_error){
		die("Connection Failed: " . $conn->connect_error);
	}
	echo "Connected established</br>";
	$sql = "SELECT rec_time,temp,wind,wind_gust,precip_today,weather FROM conditions where location='albany' order by id desc limit 5";
	$result=$conn->query($sql);	
	if ($result->num_rows >0){
		echo '<table stype="width:50%">';
		echo "<tr>";
		echo "<th>Time</th>";
		echo "<th>Weather</th>";
		echo "<th>Temp</th>";
		echo "<th>Wind</th>";
		echo "<th>Gust</th>";
		echo "<th>Precip</th></tr>";
		while($row=$result->fetch_assoc()){
			echo "<tr>";
			echo "<td>".$row["rec_time"]."</td>";
			echo "<td>".$row["weather"]."</td>";
			echo "<td>".$row["temp"]."</td>";
			echo "<td>".$row["wind"]."</td>";
			echo "<td>".$row["wind_gust"]."</td>";
			echo "<td>".$row["precip_today"]."</td>";
			echo "</tr>";
		}
		echo "</table>";	
	} else{
		echo "No Results";
	}
	$sql="select description,message from alert where expires>NOW() and location='albany' and active=1";
	$alerts=$conn->query($sql);
	if($alerts->num_rows >0){
		while($row=$alerts->fetch_assoc()){
			echo $row['description'];
			echo "</br>";
			echo $row['message'];
			echo "</br>";
		}
	}else{
		echo "No Alerts";
	}
	echo '<form method="post">';
	echo '<input type="submit" value="Dont Push this"></form>';
	$proc = shell_exec('pgrep -af python');
	if (strpos($proc,"weather") !== false){
		echo '<font color="green">Weather Service Running</font>';
	}
	else{
		echo '<font color="red">Weather Service Stopped</font>';
	}
	echo '</br>';
	if (strpos($proc,"web_service") !== false){
		echo '<font color="green">Web Service Running</font>';
	}
	else{
		echo '<font color="red">Web Service Stopped</font>';
	}

	if ($_SERVER["REQUEST_METHOD"] == "POST") {
	    // collect value of input field
		echo '<script>';
		echo 'window.alert("Oh you did it now");';
		echo '</script>';
	
	}
	echo '</br>';
	//echo '<img src="map.pgm" alt="map">';
	echo "</body>";
	echo "</html>";
$conn->close();
?>
