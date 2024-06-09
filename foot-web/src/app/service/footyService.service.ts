import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class footyService {

    constructor(private http: HttpClient) { 

    }

    obterCampeonatos(): Observable<any> {
      const url = 'http://localhost:5169/campeonato';
      return this.http.get(url);
    }
    
}