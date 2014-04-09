using UnityEngine;
using System.Collections;

public class LCMCoroutineHelper : MonoBehaviour {

	public static LCMCoroutineHelper SINGLETON;

	// Use this for initialization
	void Awake () {
		SINGLETON = this;
	}

	// Update is called once per frame
	void Update () {
	
	}
}
