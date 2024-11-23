package com.example.onetry.config;


import com.example.onetry.exception.handler.JwtExceptionHandlerFilter;
import com.example.onetry.exception.security.CustomAccessDeniedHandler;
import com.example.onetry.exception.security.CustomAuthenticationEntryPoint;
import com.example.onetry.jwt.JwtAuthFilter;
import com.example.onetry.jwt.JwtProvider;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.Collections;

@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtProvider jwtProvider;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception{
        // cors 설정
        http.cors((cors -> cors.configurationSource(configurationSource())));

        // csfr disable
        http.csrf((auth) -> auth.disable());

        // HTTP Basic 인증 방식 disable
        http.httpBasic((auth) -> auth.disable());

        //세션 설정 : STATELESS
        http.sessionManagement((session) -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS));
        //경로별 인가 작업
        http.authorizeHttpRequests((auth) -> auth
                .requestMatchers( "/login/**", "/oauth2/**", "/oauth2/authorization/**").permitAll() // OAuth2 관련 경로 허용
                .requestMatchers("/swagger-ui/**", "/v3/api-docs/**", "/swagger-resources/**", "/webjars/**").permitAll() // Swagger 관련 경로 허용
                .requestMatchers("/spring/users/sign-up", "spring/users/sing-in","/users/sign-up","/users/sign-in").permitAll()
                .requestMatchers("/certification/download","/portfolio/download").permitAll()
                .requestMatchers("/api/**").permitAll()
                .anyRequest().authenticated());

        // JWTFilter 추가
        http.addFilterBefore(new JwtExceptionHandlerFilter(), UsernamePasswordAuthenticationFilter.class);
        http.addFilterBefore(new JwtAuthFilter(jwtProvider), UsernamePasswordAuthenticationFilter.class);

        // Exception handler 추가
        http.exceptionHandling(exceptionHandling ->
                exceptionHandling
                        .accessDeniedHandler(new CustomAccessDeniedHandler())
                        .authenticationEntryPoint(new CustomAuthenticationEntryPoint()));

        return http.build();
    }

    public CorsConfigurationSource configurationSource(){
        //CORS 요청에서 허용할 헤더, 메서드, 출처(origin) 등을 설정하는 데 사용
        CorsConfiguration configuration = new CorsConfiguration();
        // 모든 "요청" 헤더를 허용하도록 * 설정, 클라이언트가 어떤 헤더를 사용해도 서버가 허용하는 것
        configuration.addAllowedHeader("*");
        // 모든 HTTP 메서드를 허용하도록 * 설정, 이는 get, post,put,delete 모든 메서드 다된다는 뜻
        configuration.addAllowedMethod("*");
        // http://localhost:3000 출처의 cors 요청을 허용한다는 뜻, 해당 URL에서만 오는 요청만 허용한다는 뜻
        configuration.setAllowedOriginPatterns(Collections.singletonList("*"));
//        configuration.addAllowedOrigin("https://dcu-speakers.store:8888");
//        configuration.addAllowedOrigin("https://2024-danpoong-team-33-fe.vercel.app");
//        configuration.addAllowedOrigin("http://localhost:5173");
        // Allow-Credentials 를 true로 설정하여 클라이언트가 자격 증명(쿠키, 인증 헤더)을 포함하여 요청할 수 있도록 함
        configuration.setAllowCredentials(true);
        // 클라이언트가 "응답" 에서 접근할 수 있는 헤더를 지정한다. ACCESS_TOKEN 헤더를 응답에 노출하도록 설정
        // 이 설정이 없으면 특정 헤더 이외엔 접근을 차단
        configuration.addExposedHeader("Authorization");

        // 특정 url 패턴에 대해 cors 구성을 적용할 수 있는 기능을 제공
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        // '/' 하위의 모든 경로 '/**' 에 대해 configuration 설정을 적용하도록 설정
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }
}