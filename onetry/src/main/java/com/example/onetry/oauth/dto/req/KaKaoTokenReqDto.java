package com.example.onetry.oauth.dto.req;

import lombok.Builder;

@Builder
public record KaKaoTokenReqDto(
        String clientId,
        String code,
        String redirectUri,
        String grantType,
        String clientSecret
) {
}
