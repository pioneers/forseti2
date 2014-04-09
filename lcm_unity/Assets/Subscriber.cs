using UnityEngine;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
public class Subscriber : MonoBehaviour {

	// Use this for initialization
	void Start () {
		StartCoroutine("Listener");
	}
	
	// Update is called once per frame
	void Update () {
	
	}

	void OnApplicationQuit() {
		running = false;
		myLCM.Close();
		StopAllCoroutines();
	}

	internal class SimpleSubscriber : LCM.LCM.LCMSubscriber
	{

		private int seq = 0;

		public void MessageReceived(LCM.LCM.LCM lcm, string channel, LCM.LCM.LCMDataInputStream dins)
		{
			Debug.Log ("RECV: " + channel);
			if (channel == "EXAMPLE")
			{
//				forseti2.health msg = new forseti2.health(dins);
//				String output = "CLCM received message of the type forseti2_health:\n";
//				output+="msg.header.seq=\t" + msg.header.seq + "\n";
//				output+="msg.header.time=\t" + msg.header.time + "\n";
//				output+="msg.uptime=\t"+msg.uptime+"\n";
//				Debug.Log (output);
//
//				forseti2.health response = new forseti2.health();
//				response.header = new forseti2.header();
//				response.header.seq = seq++;
//				TimeSpan span = DateTime.Now - new DateTime(1970, 1, 1);
//				response.header.time = span.Ticks*100;
//				response.uptime = Time.realtimeSinceStartup;
//				lcm.Publish("unity/health", response);


				exlcm.example_t msg = new exlcm.example_t(dins);
				String message = "CLCM Received message of the type example_t:\n ";
				message+=String.Format("  timestamp   = {0:D}", msg.timestamp);
				message+=String.Format("  position    = ({0:N}, {1:N}, {2:N})\n ",
				                       msg.position[0], msg.position[1], msg.position[2]);
				message+=String.Format("  orientation = ({0:N}, {1:N}, {2:N}, {3:N})\n",
				                       msg.orientation[0], msg.orientation[1], msg.orientation[2],
				                       msg.orientation[3]);
				message+=("  ranges      = [ ");
				for (int i = 0; i < msg.num_ranges; i++){
					Console.Write(" {0:D}", msg.ranges[i]);
					if (i < msg.num_ranges-1)
						Console.Write(", ");
				}
				message+=(" ]\n");
				message+=("  name         = '" + msg.name + "'\n");
				message+=("  enabled      = '" + msg.enabled + "'\n");
				Debug.Log (message);
			}
		}
	}

	Boolean running = false;
	LCM.LCM.LCM myLCM = null;

	public IEnumerator Listener()
	{
		Debug.Log ("Listener started.");
		myLCM = new LCM.LCM.LCM();
		
		myLCM.SubscribeAll(new SimpleSubscriber());
		running = true;
		while (running){
			yield return null;
		}
		Debug.Log ("listener coroutine returning!");
	}
}
