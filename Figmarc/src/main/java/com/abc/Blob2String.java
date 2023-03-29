package com.abc;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

import java.io.UnsupportedEncodingException;
import java.sql.Blob;
import java.sql.SQLException;

	public class Blob2String {

	    public static String getString(Blob blob) throws UnsupportedEncodingException, SQLException, IOException {
	        BufferedReader br = new BufferedReader(new InputStreamReader(blob.getBinaryStream(), "utf-8"));
	        String s = null;
	        StringBuilder sb = new StringBuilder();
	        while ((s = br.readLine()) != null) {
	            sb.append(s);
	        }
	        return sb.toString();
	    }
	    
	    
	    
	    
	    
	}
	
	
	

