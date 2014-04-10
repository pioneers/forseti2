using UnityEngine;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using LCM;

public class Publisher : MonoBehaviour {

	int t = 0;
	LCM.LCM.LCM myLCM;

	// Use this for initialization
	void Start () {
		Debug.Log("start");
		myLCM = LCM.LCM.LCM.Singleton;
	}
	
	// Update is called once per frame
	void Update () {
		t++;
		if (t > 60){
			exlcm.example_t msg = new exlcm.example_t();
			TimeSpan span = DateTime.Now - new DateTime(1970, 1, 1);
			msg.timestamp = span.Ticks * 100;
			msg.position = new double[] { 1, 2, 3 };
			msg.orientation = new double[] { 1, 0, 0, 0 };
			msg.num_ranges = 15;
			msg.ranges = new short[msg.num_ranges];
			for (int i = 0; i < msg.num_ranges; i++)
			{
				msg.ranges[i] = (short) i;
			}
			msg.name = "example string";
			msg.enabled = true;
			
			myLCM.Publish("EXAMPLE", msg);
			Debug.Log("update" + Time.time);
			t=0;
		}
		
	}
}
