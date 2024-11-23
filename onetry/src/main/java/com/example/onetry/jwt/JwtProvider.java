package com.example.onetry.jwt;

import io.jsonwebtoken.Jwts;
import jakarta.annotation.PostConstruct;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.log4j.Log4j2;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.util.Date;

@Log4j2
@Component
@RequiredArgsConstructor
public class JwtProvider {
    private final UserDetailsService userDetailsService;

    @Value("${spring.jwt.secret}")
    private String secret;
    private SecretKey secretKey;

    @Value("${spring.jwt.access-token-valid-time}")
    private Long accessTokenValidTime;

    @Value("${spring.jwt.refresh-token-valid-time}")
    private Long refreshTokenValidTime;

    @PostConstruct // 의존성 주입이 완료된 직후에 자동으로 호출
    // 다른 패키지에서 사용 할 필요가 없기 떄문
    protected void init(){
        // secret 문자열을바이트 배열로 -> SecretKeySpec은 바이트 배열 기반으로 sha-256 알고리즘을 적용하여 대칭키를 생성
        // Jwts.SIG.HS256.key().build().getAlgorithm() 알고리즘을 지정하여 JWT 서명 알고리즘을 설정. secretKey 는 이후 jwt 생성 및 검증에 사용
        secretKey = new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), Jwts.SIG.HS256.key().build().getAlgorithm());
    }

    // 토큰 생성
    public String createAccessToken(String email, String role, String name, Long userId){
        return Jwts.builder()
                .claim("userId", userId)
                .claim("name", name)
                .claim("email", email)
                .claim("role",role)
                .issuedAt(new Date(System.currentTimeMillis()))
                .expiration(new Date(System.currentTimeMillis() + accessTokenValidTime))
                .signWith(secretKey)
                .compact();
    }
    public String createRefreshToken(String email, String role, String name, Long userId){
        return Jwts.builder()
                .claim("userId", userId)
                .claim("name", name)
                .claim("email", email)
                .claim("role",role)
                .issuedAt(new Date(System.currentTimeMillis()))
                .expiration(new Date(System.currentTimeMillis() + refreshTokenValidTime))
                .signWith(secretKey)
                .compact();
    }

    // token을 받아 인증 객체를 생성, Authentication 객체는 사용자 정보와 권한을 담고있다.
    // JWT 필터에서 사용
    public Authentication getAuthentication(String token){
        // UserDetails 객체를 불러온다.
        UserDetails userDetails = userDetailsService.loadUserByUsername(getEmail(token));
        log.info("[getAuthenticaton] UserDetails email : {}", userDetails.getUsername());
        // UserDetails, 비밀번호, 사용자 권한 정보 를 매개변수로 Authentication 객체를 생성한다.
        return new UsernamePasswordAuthenticationToken(userDetails,"",userDetails.getAuthorities());
    }

    // bearer 토큰의 순수 토큰을 분리하였습니다.
    public String getPureToken(String bearerToken){
        if(bearerToken == null || !bearerToken.startsWith("[Bearer "))return null;
        String pureToken = bearerToken.substring(1, bearerToken.length()-1);
        return pureToken.substring("Bearer ".length()).trim();
    }

    public String getTokenFromHeader(HttpServletRequest request){
        String token = request.getHeader("Authorization");
        log.info("요청에 담긴 토큰 : {}", token);
        if(token == null || !token.startsWith("Bearer "))return null;
        return token.substring("Bearer ".length()).trim();
    }
    public Long getUserId(String token){
        return Jwts.parser().verifyWith(secretKey).build().parseSignedClaims(token).getPayload().get("userId", Long.class);
    }

    public String getEmail(String token){
        return Jwts.parser().verifyWith(secretKey).build().parseSignedClaims(token).getPayload().get("email", String.class);
    }

    public String getName(String token){
        return Jwts.parser().verifyWith(secretKey).build().parseSignedClaims(token).getPayload().get("name", String.class);
    }

    public String getRole(String token) {
        return Jwts.parser().verifyWith(secretKey).build().parseSignedClaims(token).getPayload().get("role", String.class);
    }

    public Boolean isExpired(String token) {
        return Jwts.parser().verifyWith(secretKey).build().parseSignedClaims(token).getPayload().getExpiration().before(new Date());
    }
}
